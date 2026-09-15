import os
import sys
import pandas as pd
from datetime import datetime

# Adjust Python path for backend package resolution
# File is at: smart-food-waste-predictor/backend/app/database/init_db.py
current_file = os.path.abspath(__file__)
database_dir = os.path.dirname(current_file)
app_dir = os.path.dirname(database_dir)
backend_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(backend_dir)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import engine, Base, SessionLocal
from app.models.entities import MealRecord, PredictionRecord, ModelMetric

def init_and_seed_db():
    print("=====================================================")
    print("       PHASE 7: DATABASE INIT & HISTORICAL SEED       ")
    print("=====================================================\n")
    
    # 1. Create tables
    print("Creating database schema (tables & constraints)...")
    Base.metadata.create_all(bind=engine)
    print("[PASS] Tables created: meal_records, predictions, model_metrics")
    
    db = SessionLocal()
    try:
        count = db.query(MealRecord).count()
        if count > 0:
            print(f"Database already contains {count} records. Resetting for clean seed...")
            db.query(MealRecord).delete()
            db.query(ModelMetric).delete()
            db.commit()
            
        csv_path = os.path.join(project_dir, "ml", "data", "canteen_operations_180d.csv")
        print(f"Reading dataset from: {csv_path}")
        df = pd.read_csv(csv_path)
        
        print(f"Seeding {len(df)} operational records into meal_records table...")
        records = []
        for _, row in df.iterrows():
            record = MealRecord(
                date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                day_of_week=row["day_of_week"],
                attendance=int(row["attendance"]),
                meals_prepared=int(row["meals_prepared"]),
                meals_consumed=int(row["meals_consumed"]),
                waste=int(row["waste"]),
                is_holiday=int(row.get("is_holiday", 0)),
                is_exam_day=int(row.get("is_exam_day", 0)),
                is_event_day=int(row.get("is_event_day", 0))
            )
            records.append(record)
            
        db.bulk_save_objects(records)
        db.commit()
        
        seeded_count = db.query(MealRecord).count()
        print(f"[PASS] Successfully seeded {seeded_count} meal_records!")
        
        # Seed model benchmark metrics
        metrics = [
            ModelMetric(model_name="Gradient Boosting Regressor", mae=5.82, rmse=6.83, r2=0.9960, is_active=True),
            ModelMetric(model_name="Ridge Regression", mae=6.32, rmse=7.65, r2=0.9950, is_active=False),
            ModelMetric(model_name="Linear Regression", mae=6.35, rmse=7.66, r2=0.9950, is_active=False),
            ModelMetric(model_name="Random Forest Regressor", mae=6.51, rmse=7.61, r2=0.9950, is_active=False),
            ModelMetric(model_name="Day-of-Week Naive Baseline", mae=16.00, rmse=19.29, r2=0.9681, is_active=False),
        ]
        db.bulk_save_objects(metrics)
        db.commit()
        print(f"[PASS] Successfully registered {len(metrics)} model benchmark metrics in model_metrics table.")
        
        # Verification queries
        first_row = db.query(MealRecord).order_by(MealRecord.date.asc()).first()
        last_row = db.query(MealRecord).order_by(MealRecord.date.desc()).first()
        print("\n--- Integrity Verification Check ---")
        print(f"Oldest Record: {first_row.date} ({first_row.day_of_week}) | Attendance: {first_row.attendance}, Prepared: {first_row.meals_prepared}, Consumed: {first_row.meals_consumed}, Waste: {first_row.waste}")
        print(f"Latest Record: {last_row.date} ({last_row.day_of_week}) | Attendance: {last_row.attendance}, Prepared: {last_row.meals_prepared}, Consumed: {last_row.meals_consumed}, Waste: {last_row.waste}")
        print("\n[SUCCESS] Database initialized, tables verified, and historical data seeded!")
        print("=====================================================")
    finally:
        db.close()

if __name__ == "__main__":
    init_and_seed_db()
