# Hackathon Presentation: Smart Food Waste Predictor (PS-2Y-01)
**Track:** 2nd Year Track — Zero Hunger | **SDG:** SDG 2

---

## Slide 1: Title & Team
- **Project Title:** Smart Food Waste Predictor
- **Tagline:** Data-Driven Meal Forecasting & Waste Elimination for College Canteens
- **Domain:** AI for Social Good / Sustainable Resource Management

---

## Slide 2: The Problem
- College canteens prepare meals based on **gut-feeling and arbitrary estimates**.
- **Result:**
  - Up to **13.6% food waste** on drop-off days (Fridays).
  - High operational food loss (thousands of meals wasted per semester).
  - Risk of stockouts (under-cooking) vs. over-cooking.

---

## Slide 3: Our Solution
- A full-stack web application that answers three questions:
  1. **What happened?** (Historical attendance, meals prepared, consumed, and waste).
  2. **What will happen tomorrow?** (AI predicted meal demand).
  3. **What should the canteen do?** (Recommended preparation target + safety buffer + waste directives).

---

## Slide 4: System Architecture
- **Frontend:** React 19, Vite, Tailwind CSS, Recharts
- **Backend:** Python, FastAPI, Pydantic, Uvicorn
- **ML Engine:** scikit-learn, joblib, Gradient Boosting Regressor
- **Database:** PostgreSQL / SQLite (ACID compliant with physical constraints)

---

## Slide 5: Machine Learning & Zero Data Leakage
- **Features:** Expected Attendance, Day of Week, 7-Day Rolling Demand, Lag Demand ($t-1$), Historical Weekday Means.
- **Strict Chronological Split:** 144 days training $\rightarrow$ 36 days unseen testing (no future leakage).
- **Baseline Benchmark:** Day-of-Week historical mean (**MAE: 16.00 meals**).
- **Winning Model:** Gradient Boosting Regressor (**MAE: 5.82 meals, +63.6% improvement**).

---

## Slide 6: The Innovation — Beyond Raw Predictions
1. **Dynamic Safety Buffer:** $\text{Predicted Demand} + (1.0 \times \sigma_{\text{residual}}) \rightarrow \text{Recommended Prep}$.
2. **Transparent Explanations:** Real data factors driving the forecast.
3. **Friday Wastage Alert:** Flags structural 13.6% waste trap and advises portion control.
4. **Closed-Loop Feedback:** Evening actuals link to morning predictions to calculate prediction error.

---

## Slide 7: Live Demo Flow
1. **Dashboard:** View live KPIs and 30-day operational trends.
2. **Tomorrow Forecast:** Input expected attendance $\rightarrow$ Get recommended preparation.
3. **Sensitivity Simulator:** Test "What-If" attendance changes ($\pm 10\%$).
4. **Daily Data Entry:** Log actual numbers $\rightarrow$ System verifies physical constraints and tracks error.

---

## Slide 8: Future Scope
- Multi-canteen centralized dashboard across university campuses.
- Automated POS / Turnstile attendance API integration.
- Recipe & ingredient-level automated procurement forecasting.
