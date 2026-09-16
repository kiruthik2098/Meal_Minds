import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

current_file = os.path.abspath(__file__)
database_dir = os.path.dirname(current_file)
app_dir = os.path.dirname(database_dir)
backend_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(backend_dir)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.connection import engine, Base, SessionLocal
from app.models.entities import MealRecord, PredictionRecord, ModelMetric

# Multipliers & characteristics for each meal slot
SLOT_CONFIG = {
    "breakfast": {"att_ratio": 0.60, "consumption_rate": 0.88, "waste_buffer": (1.05, 1.12)},
    "lunch":     {"att_ratio": 1.00, "consumption_rate": 0.92, "waste_buffer": (1.06, 1.15)},
    "snacks":    {"att_ratio": 0.45, "consumption_rate": 0.85, "waste_buffer": (1.04, 1.10)},
    "dinner":    {"att_ratio": 0.75, "consumption_rate": 0.90, "waste_buffer": (1.05, 1.14)}
}

def reseed_multislot_dataset():
    print("Rebuilding database with comprehensive multi-slot data (Breakfast, Lunch, Snacks, Dinner)...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    np.random.seed(42)
    try:
        csv_path = os.path.join(project_dir, "ml", "data", "canteen_operations_180d.csv")
        df = pd.read_csv(csv_path)
        
        records = []
        for _, row in df.iterrows():
            rec_date = datetime.strptime(row["date"], "%Y-%m-%d").date()
            day_name = row["day_of_week"]
            base_att = int(row["attendance"])
            is_hol = int(row.get("is_holiday", 0))
            is_ex = int(row.get("is_exam_day", 0))
            is_ev = int(row.get("is_event_day", 0))
            
            for slot, cfg in SLOT_CONFIG.items():
                # Scale attendance by slot
                slot_att = max(15, int(round(base_att * cfg["att_ratio"] * np.random.uniform(0.95, 1.05))))
                
                # Consumed meals
                cons_rate = cfg["consumption_rate"] * np.random.uniform(0.96, 1.02)
                meals_consumed = max(10, int(round(slot_att * cons_rate)))
                
                # Friday over-preparation pattern specifically on lunch & dinner
                if day_name == "Friday" and slot in ["lunch", "dinner"]:
                    prep_mult = np.random.uniform(1.12, 1.24)
                else:
                    prep_mult = np.random.uniform(cfg["waste_buffer"][0], cfg["waste_buffer"][1])
                    
                meals_prepared = int(round(meals_consumed * prep_mult))
                if meals_prepared < meals_consumed:
                    meals_prepared = meals_consumed + np.random.randint(2, 6)
                    
                waste = meals_prepared - meals_consumed
                
                records.append(MealRecord(
                    date=rec_date,
                    meal_type=slot,
                    day_of_week=day_name,
                    attendance=slot_att,
                    meals_prepared=meals_prepared,
                    meals_consumed=meals_consumed,
                    waste=waste,
                    is_holiday=is_hol,
                    is_exam_day=is_ex,
                    is_event_day=is_ev
                ))
                
        db.bulk_save_objects(records)
        db.commit()
        print(f"[SUCCESS] Seeded {len(records)} total records across all 4 meal slots (Breakfast, Lunch, Snacks, Dinner)!")
        
        metrics = [
            ModelMetric(model_name="Gradient Boosting Regressor", mae=5.82, rmse=6.83, r2=0.9960, is_active=True),
            ModelMetric(model_name="Ridge Regression", mae=6.32, rmse=7.65, r2=0.9950, is_active=False),
            ModelMetric(model_name="Linear Regression", mae=6.35, rmse=7.66, r2=0.9950, is_active=False),
            ModelMetric(model_name="Random Forest Regressor", mae=6.51, rmse=7.61, r2=0.9950, is_active=False),
            ModelMetric(model_name="Day-of-Week Naive Baseline", mae=16.00, rmse=19.29, r2=0.9681, is_active=False),
        ]
        db.bulk_save_objects(metrics)
        db.commit()
        print("[SUCCESS] Model metrics restored.")
    finally:
        db.close()

if __name__ == "__main__":
    reseed_multislot_dataset()
