import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_baseline():
    print("=====================================================")
    print("            PHASE 4: ML BASELINE BENCHMARK           ")
    print("=====================================================\n")
    
    # Load dataset
    data_path = os.path.join(os.path.dirname(__file__), "data", "canteen_operations_180d.csv")
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    # 1. Chronological Train/Test Split (80% Train, 20% Test)
    split_idx = int(len(df) * 0.80)
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()
    
    print("--- 1. Chronological Split Strategy ---")
    print(f"Total Records:      {len(df)} days")
    print(f"Training Window:    {train_df['date'].min().strftime('%Y-%m-%d')} to {train_df['date'].max().strftime('%Y-%m-%d')} ({len(train_df)} days)")
    print(f"Testing Window:     {test_df['date'].min().strftime('%Y-%m-%d')} to {test_df['date'].max().strftime('%Y-%m-%d')} ({len(test_df)} days)")
    print("Why temporal split? Shuffling time-series data leaks future patterns into the past.\n")
    
    # 2. Baseline Model Definition:
    # Rule: Predict tomorrow's meal demand as the historical average for that SAME day of week from training data.
    weekday_means = train_df.groupby("day_of_week")["meals_consumed"].mean().to_dict()
    
    print("--- 2. Baseline Learned Look-Up (Train Set Day-of-Week Averages) ---")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        print(f"  {day:9s}: {weekday_means[day]:.1f} meals")
        
    # 3. Test Set Predictions
    y_test_actual = test_df["meals_consumed"].values
    y_test_pred = test_df["day_of_week"].map(weekday_means).values
    
    # 4. Metrics Evaluation
    mae = mean_absolute_error(y_test_actual, y_test_pred)
    rmse = np.sqrt(mean_squared_error(y_test_actual, y_test_pred))
    r2 = r2_score(y_test_actual, y_test_pred)
    
    print("\n--- 3. Baseline Performance Metrics (Test Set Benchmark) ---")
    print(f"  MAE  (Mean Absolute Error):     {mae:.2f} meals")
    print(f"  RMSE (Root Mean Squared Error): {rmse:.2f} meals")
    print(f"  R2   (Explained Variance):      {r2:.4f}")
    
    print("\n--- 4. Plain-English Metric Explanations ---")
    print(f"  • MAE = {mae:.1f}: On average, a simple day-of-week average is off by approximately {mae:.1f} meals.")
    print("  • Why ML is needed: The baseline cannot adjust for sudden attendance fluctuations, event surges, or exams.")
    print("  • Our Goal for Phase 5 ML Models: Outperform MAE < 15 and achieve R2 > 0.95.\n")
    
    return {
        "model": "Day-of-Week Naive Baseline",
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4)
    }

if __name__ == "__main__":
    evaluate_baseline()
