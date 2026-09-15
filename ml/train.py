import os
import sys
import pandas as pd
import numpy as np
import joblib

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure sibling import works
sys.path.append(os.path.dirname(__file__))
from preprocessing.features import build_features

def train_and_evaluate_models():
    print("=====================================================")
    print("        PHASE 5: ML MODEL TRAINING & COMPARISON       ")
    print("=====================================================\n")
    
    # 1. Load dataset
    data_path = os.path.join(os.path.dirname(__file__), "data", "canteen_operations_180d.csv")
    df = pd.read_csv(data_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    # 2. Chronological Split (80% Train, 20% Test)
    split_idx = int(len(df) * 0.80)
    train_raw = df.iloc[:split_idx].copy()
    test_raw = df.iloc[split_idx:].copy()
    
    # 3. Feature Engineering with zero leakage
    train_feat, weekday_means = build_features(train_raw, is_training=True)
    test_feat, _ = build_features(test_raw, is_training=False, historical_weekday_means=weekday_means)
    
    cat_features = ["day_of_week"]
    num_features = [
        "attendance",
        "is_holiday",
        "is_exam_day",
        "is_event_day",
        "lag_1_demand",
        "lag_1_waste",
        "rolling_7_demand",
        "rolling_7_attendance",
        "weekday_historical_mean",
        "recent_demand_trend"
    ]
    all_feature_cols = cat_features + num_features
    target_col = "meals_consumed"
    
    X_train = train_feat[all_feature_cols]
    y_train = train_feat[target_col].values
    X_test = test_feat[all_feature_cols]
    y_test = test_feat[target_col].values
    
    print(f"Dataset Split: {len(X_train)} Train Days | {len(X_test)} Test Days")
    print(f"Features in Model ({len(all_feature_cols)} total): {all_feature_cols}\n")
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_features),
            ("num", "passthrough", num_features)
        ]
    )
    
    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42, max_depth=6),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=3, learning_rate=0.08)
    }
    
    baseline_mae = 16.00
    baseline_rmse = 19.29
    baseline_r2 = 0.9681
    
    results = []
    trained_pipelines = {}
    
    print("--- Model Evaluation on Unseen Test Window ---")
    for name, regressor in models.items():
        pipe = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", regressor)])
        pipe.fit(X_train, y_train)
        
        y_pred = pipe.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        mae_imprv = ((baseline_mae - mae) / baseline_mae) * 100
        
        results.append({
            "Model": name,
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 4),
            "MAE Improvement vs Baseline": f"+{mae_imprv:.1f}%" if mae_imprv > 0 else f"{mae_imprv:.1f}%"
        })
        trained_pipelines[name] = {
            "pipeline": pipe,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "residuals": (y_test - y_pred)
        }
        
    results_df = pd.DataFrame(results).sort_values("MAE").reset_index(drop=True)
    print(results_df.to_string(index=False))
    
    best_model_name = results_df.iloc[0]["Model"]
    best_pipe_info = trained_pipelines[best_model_name]
    best_mae = best_pipe_info["mae"]
    best_rmse = best_pipe_info["rmse"]
    best_r2 = best_pipe_info["r2"]
    
    residual_std = float(np.std(best_pipe_info["residuals"]))
    
    print(f"\n[WINNER] WINNING MODEL: {best_model_name}")
    print(f"  * Test MAE:  {best_mae:.2f} meals (Down from 16.00 in Baseline!)")
    print(f"  * Test RMSE: {best_rmse:.2f} meals")
    print(f"  * Test R2:   {best_r2:.4f}")
    print(f"  * Residual Std Dev (Safety Buffer basis): +/-{residual_std:.2f} meals")
    
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_artifact_path = os.path.join(models_dir, "best_demand_model.joblib")
    
    model_payload = {
        "model_name": best_model_name,
        "pipeline": best_pipe_info["pipeline"],
        "weekday_means": weekday_means,
        "feature_cols": all_feature_cols,
        "metrics": {
            "mae": round(best_mae, 2),
            "rmse": round(best_rmse, 2),
            "r2": round(best_r2, 4),
            "residual_std": round(residual_std, 2)
        },
        "baseline_metrics": {
            "mae": baseline_mae,
            "rmse": baseline_rmse,
            "r2": baseline_r2
        },
        "all_model_results": results
    }
    
    joblib.dump(model_payload, model_artifact_path)
    print(f"\n[SAVED] Winning model artifact successfully exported to:")
    print(f"  -> {model_artifact_path}")
    print("=====================================================")

if __name__ == "__main__":
    train_and_evaluate_models()
