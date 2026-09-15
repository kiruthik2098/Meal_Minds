import os
import sys
import pandas as pd
import joblib

def predict_single_day(date_str, expected_attendance, is_holiday=0, is_exam_day=0, is_event_day=0):
    """
    Takes operational parameters for tomorrow and returns raw model prediction.
    """
    model_path = os.path.join(os.path.dirname(__file__), "models", "best_demand_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model artifact not found. Run train.py first.")
        
    payload = joblib.load(model_path)
    pipe = payload["pipeline"]
    weekday_means = payload["weekday_means"]
    
    # Read latest history to extract real lag & rolling features
    data_path = os.path.join(os.path.dirname(__file__), "data", "canteen_operations_180d.csv")
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    # Target date day of week
    target_dt = pd.to_datetime(date_str)
    day_name = target_dt.strftime("%A")
    
    # Calculate real-world lag features from latest historical window
    lag_1_demand = float(df["meals_consumed"].iloc[-1])
    lag_1_waste = float(df["waste"].iloc[-1])
    rolling_7_demand = float(df["meals_consumed"].iloc[-7:].mean())
    rolling_7_attendance = float(df["attendance"].iloc[-7:].mean())
    weekday_historical_mean = float(weekday_means.get(day_name, df["meals_consumed"].mean()))
    recent_demand_trend = float(rolling_7_demand - weekday_historical_mean)
    
    input_df = pd.DataFrame([{
        "day_of_week": day_name,
        "attendance": expected_attendance,
        "is_holiday": is_holiday,
        "is_exam_day": is_exam_day,
        "is_event_day": is_event_day,
        "lag_1_demand": lag_1_demand,
        "lag_1_waste": lag_1_waste,
        "rolling_7_demand": rolling_7_demand,
        "rolling_7_attendance": rolling_7_attendance,
        "weekday_historical_mean": weekday_historical_mean,
        "recent_demand_trend": recent_demand_trend
    }])
    
    raw_prediction = float(pipe.predict(input_df)[0])
    
    return {
        "date": date_str,
        "day_of_week": day_name,
        "expected_attendance": expected_attendance,
        "predicted_demand": round(raw_prediction, 1),
        "model_name": payload["model_name"],
        "model_mae": payload["metrics"]["mae"],
        "residual_std": payload["metrics"]["residual_std"],
        "weekday_historical_mean": round(weekday_historical_mean, 1)
    }

if __name__ == "__main__":
    test_result = predict_single_day("2026-08-28", expected_attendance=440)
    print("=== Single-Day Prediction Test ===")
    for k, v in test_result.items():
        print(f"  {k:25s}: {v}")
