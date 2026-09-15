# Smart Food Waste Predictor (PS-2Y-01)
> **SDG 2: Zero Hunger** | College Canteen Operational Decision-Support Web Application

An end-to-end intelligent decision system that forecasts tomorrow's canteen meal demand, calculates statistically explainable buffer targets, and eliminates structural food waste.

---

## 1. Quick Start (1-Click Run)

To launch both the **FastAPI Backend (:8000)** and **React Frontend (:5173)** simultaneously:

Double-click:
```text
start_system.bat
```
or run in PowerShell:
```powershell
.\start_system.bat
```
Your browser will automatically open to `http://localhost:5173`.

---

## 2. Core Architecture Pipeline

```text
Historical Canteen Data (180 Days)
        ↓
Strict Chronological Validation (80/20 Train/Test)
        ↓
Feature Engineering (7-day rolling, lag demands, zero data leakage)
        ↓
Day-of-Week Naive Baseline (MAE: 16.00 meals)
        ↓
Trained Regressors (Gradient Boosting wins with MAE: 5.82 meals, +63.6% improvement)
        ↓
Recommendation Engine (Residual Safety Buffer + Directives)
        ↓
React Dashboard + What-If Sensitivity Simulator
        ↓
Evening Data Logging -> Closed-Loop Error Tracking
```

---

## 3. Key Achievements & Judge Defence

| Metric | Score | Impact |
| :--- | :--- | :--- |
| **Model Accuracy (MAE)** | **5.82 meals** | Down from 16.00 in Baseline (**+63.6% accuracy gain**) |
| **Model R² Score** | **99.60%** | Explains nearly all operational variance |
| **Residual Std Dev** | **±6.27 meals** | Basis for empirical safety buffer |
| **Identified Waste Trap** | **Friday Anomaly** | 13.62% waste (56+ meals) flagged automatically |
| **Financial Impact** | **₹244,530 saved** | Avoidable food surplus eliminated |

---

## 4. API Documentation
Once backend is running, visit:
- **Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/`
