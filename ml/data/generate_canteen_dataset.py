import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_canteen_data(start_date="2026-03-01", days=180, random_seed=42):
    np.random.seed(random_seed)
    records = []
    current = datetime.strptime(start_date, "%Y-%m-%d")
    
    day_attendance_base = {
        "Monday": 440,
        "Tuesday": 455,
        "Wednesday": 450,
        "Thursday": 445,
        "Friday": 385,
        "Saturday": 230,
        "Sunday": 130
    }
    
    for i in range(days):
        dt = current + timedelta(days=i)
        day_name = dt.strftime("%A")
        date_str = dt.strftime("%Y-%m-%d")
        
        is_holiday = False
        is_exam_day = False
        is_event_day = False
        
        day_index = i
        if 60 <= day_index <= 74 and day_name not in ["Sunday"]:
            is_exam_day = True
        elif day_index in [25, 26, 110, 111]:
            is_event_day = True
        elif day_index in [15, 80, 140]:
            is_holiday = True
            
        base_att = day_attendance_base[day_name]
        
        if is_holiday:
            attendance = int(np.random.normal(50, 10))
            attendance = max(20, attendance)
        elif is_event_day:
            attendance = int(np.random.normal(base_att * 1.35, 20))
        elif is_exam_day:
            attendance = int(np.random.normal(base_att * 0.90, 15))
        else:
            attendance = int(np.random.normal(base_att, 18))
        
        attendance = max(10, attendance)
        
        consumption_rate = np.random.uniform(0.88, 0.94)
        meals_consumed = int(round(attendance * consumption_rate))
        
        if is_holiday:
            prep_buffer_rate = np.random.uniform(1.05, 1.15)
        elif day_name == "Friday":
            prep_buffer_rate = np.random.uniform(1.11, 1.22)
        elif is_event_day:
            prep_buffer_rate = np.random.uniform(1.08, 1.20)
        else:
            prep_buffer_rate = np.random.uniform(1.04, 1.12)
            
        meals_prepared = int(round(meals_consumed * prep_buffer_rate))
        if meals_prepared < meals_consumed:
            meals_prepared = meals_consumed + np.random.randint(2, 8)
            
        waste = meals_prepared - meals_consumed
        
        records.append({
            "date": date_str,
            "day_of_week": day_name,
            "attendance": attendance,
            "meals_prepared": meals_prepared,
            "meals_consumed": meals_consumed,
            "waste": waste,
            "is_holiday": 1 if is_holiday else 0,
            "is_exam_day": 1 if is_exam_day else 0,
            "is_event_day": 1 if is_event_day else 0
        })
        
    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_canteen_data(start_date="2026-03-01", days=180)
    output_path = os.path.join("ml", "data", "canteen_operations_180d.csv")
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} records at {output_path}")
