import os
import sys
import json
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional

# Adjust path for sibling ml import
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
project_dir = os.path.dirname(backend_dir)
ml_dir = os.path.join(project_dir, "ml")
if ml_dir not in sys.path:
    sys.path.insert(0, ml_dir)

from recommend import generate_recommendations
from ..models.entities import MealRecord, PredictionRecord, ModelMetric
from ..schemas.dto import MealRecordCreate, PredictionRequest, DashboardStatistics, WeekdayPattern

class CanteenService:

    @staticmethod
    def get_records(db: Session, limit: int = 100, offset: int = 0) -> List[MealRecord]:
        return db.query(MealRecord).order_by(MealRecord.date.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_record_by_id(db: Session, record_id: int) -> Optional[MealRecord]:
        return db.query(MealRecord).filter(MealRecord.id == record_id).first()

    @staticmethod
    def create_record(db: Session, record_in: MealRecordCreate) -> MealRecord:
        # Check duplicate date
        existing = db.query(MealRecord).filter(MealRecord.date == record_in.date).first()
        if existing:
            raise ValueError(f"Record for date {record_in.date} already exists.")

        day_name = record_in.date.strftime("%A")
        waste = record_in.meals_prepared - record_in.meals_consumed

        new_record = MealRecord(
            date=record_in.date,
            day_of_week=day_name,
            attendance=record_in.attendance,
            meals_prepared=record_in.meals_prepared,
            meals_consumed=record_in.meals_consumed,
            waste=waste,
            is_holiday=record_in.is_holiday,
            is_exam_day=record_in.is_exam_day,
            is_event_day=record_in.is_event_day
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        # Closed Loop Feedback: If a prediction was logged for this date, link actuals!
        pred = db.query(PredictionRecord).filter(PredictionRecord.prediction_date == record_in.date).first()
        if pred:
            pred.actual_demand = float(record_in.meals_consumed)
            pred.prediction_error = round(float(record_in.meals_consumed) - pred.predicted_demand, 2)
            db.commit()

        return new_record

    @staticmethod
    def delete_record(db: Session, record_id: int) -> bool:
        record = db.query(MealRecord).filter(MealRecord.id == record_id).first()
        if not record:
            return False
        db.delete(record)
        db.commit()
        return True

    @staticmethod
    def predict_and_recommend(db: Session, req: PredictionRequest) -> dict:
        date_str = req.date.strftime("%Y-%m-%d")
        rec_data = generate_recommendations(
            date_str=date_str,
            expected_attendance=req.expected_attendance,
            is_holiday=req.is_holiday,
            is_exam_day=req.is_exam_day,
            is_event_day=req.is_event_day
        )

        # Persist prediction in database
        # Check if actual record already exists for this date
        actual_rec = db.query(MealRecord).filter(MealRecord.date == req.date).first()
        actual_val = float(actual_rec.meals_consumed) if actual_rec else None
        error_val = round(actual_val - rec_data["predicted_demand"], 2) if actual_val is not None else None

        pred_entry = PredictionRecord(
            prediction_date=req.date,
            day_of_week=rec_data["day_of_week"],
            expected_attendance=req.expected_attendance,
            predicted_demand=rec_data["predicted_demand"],
            safety_buffer=rec_data["safety_buffer"],
            recommended_preparation=rec_data["recommended_preparation"],
            model_name=rec_data["model_name"],
            actual_demand=actual_val,
            prediction_error=error_val,
            explanations=json.dumps(rec_data["explanations"]),
            suggestions=json.dumps(rec_data["suggestions"])
        )
        db.add(pred_entry)
        db.commit()
        db.refresh(pred_entry)

        rec_data["id"] = pred_entry.id
        rec_data["actual_demand"] = actual_val
        rec_data["prediction_error"] = error_val
        return rec_data

    @staticmethod
    def get_predictions(db: Session, limit: int = 50) -> List[dict]:
        preds = db.query(PredictionRecord).order_by(PredictionRecord.prediction_date.desc()).limit(limit).all()
        result = []
        for p in preds:
            result.append({
                "id": p.id,
                "date": p.prediction_date,
                "day_of_week": p.day_of_week,
                "expected_attendance": p.expected_attendance,
                "predicted_demand": p.predicted_demand,
                "safety_buffer": p.safety_buffer,
                "recommended_preparation": p.recommended_preparation,
                "model_name": p.model_name,
                "model_mae": 5.82,
                "actual_demand": p.actual_demand,
                "prediction_error": p.prediction_error,
                "explanations": json.loads(p.explanations) if p.explanations else [],
                "suggestions": json.loads(p.suggestions) if p.suggestions else []
            })
        return result

    @staticmethod
    def get_dashboard_statistics(db: Session) -> DashboardStatistics:
        records = db.query(MealRecord).all()
        total_records = len(records)
        if total_records == 0:
            return DashboardStatistics(
                total_records=0, total_meals_prepared=0, total_meals_consumed=0, total_waste=0,
                overall_waste_percentage=0.0, avg_daily_attendance=0.0, avg_daily_demand=0.0,
                avg_daily_waste=0.0, estimated_cost_wasted=0.0, active_model_name="N/A",
                active_model_mae=0.0, baseline_mae=16.0, mae_improvement_pct=0.0
            )

        total_prep = sum(r.meals_prepared for r in records)
        total_cons = sum(r.meals_consumed for r in records)
        total_waste = sum(r.waste for r in records)
        waste_pct = round((total_waste / total_prep * 100) if total_prep > 0 else 0.0, 2)

        avg_att = round(sum(r.attendance for r in records) / total_records, 1)
        avg_dem = round(total_cons / total_records, 1)
        avg_wst = round(total_waste / total_records, 1)
        cost_wasted = round(total_waste * 45.0, 2)  # Assumes INR 45 per meal cost

        active_model = db.query(ModelMetric).filter(ModelMetric.is_active == True).first()
        active_name = active_model.model_name if active_model else "Gradient Boosting Regressor"
        active_mae = active_model.mae if active_model else 5.82
        baseline_mae = 16.00
        imprv = round(((baseline_mae - active_mae) / baseline_mae) * 100, 1)

        return DashboardStatistics(
            total_records=total_records,
            total_meals_prepared=total_prep,
            total_meals_consumed=total_cons,
            total_waste=total_waste,
            overall_waste_percentage=waste_pct,
            avg_daily_attendance=avg_att,
            avg_daily_demand=avg_dem,
            avg_daily_waste=avg_wst,
            estimated_cost_wasted=cost_wasted,
            active_model_name=active_name,
            active_model_mae=active_mae,
            baseline_mae=baseline_mae,
            mae_improvement_pct=imprv
        )

    @staticmethod
    def get_weekday_patterns(db: Session) -> List[WeekdayPattern]:
        records = db.query(MealRecord).all()
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_groups = {day: [] for day in dow_order}

        for r in records:
            if r.day_of_week in dow_groups:
                dow_groups[r.day_of_week].append(r)

        patterns = []
        for day in dow_order:
            group = dow_groups[day]
            if not group:
                continue
            n = len(group)
            avg_att = round(sum(r.attendance for r in group) / n, 1)
            avg_prep = round(sum(r.meals_prepared for r in group) / n, 1)
            avg_cons = round(sum(r.meals_consumed for r in group) / n, 1)
            avg_waste = round(sum(r.waste for r in group) / n, 1)
            waste_pct = round((avg_waste / avg_prep * 100) if avg_prep > 0 else 0.0, 2)
            patterns.append(WeekdayPattern(
                day_of_week=day,
                avg_attendance=avg_att,
                avg_prepared=avg_prep,
                avg_consumed=avg_cons,
                avg_waste=avg_waste,
                waste_percentage=waste_pct
            ))
        return patterns

    @staticmethod
    def get_model_metrics(db: Session) -> List[ModelMetric]:
        return db.query(ModelMetric).order_by(ModelMetric.mae.asc()).all()
