@echo off
echo ========================================================
echo   STARTING SMART FOOD WASTE PREDICTOR (BACKEND + FRONTEND)
echo ========================================================
start "Canteen Backend [FastAPI :8001]" cmd /k "cd /d C:\Users\91638\SIH26187\smart-food-waste-predictor\backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
timeout /t 2 >nul
start "Canteen Frontend [React Vite :5173]" cmd /k "cd /d C:\Users\91638\SIH26187\smart-food-waste-predictor\frontend && npm run dev"
echo Servers launched! Browser will open automatically at http://localhost:5173
timeout /t 2 >nul
start http://localhost:5173
