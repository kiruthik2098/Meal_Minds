from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from ..database.connection import get_db
from ..schemas.dto import (
    MealRecordCreate, MealRecordResponse, PredictionRequest,
    PredictionResponse, DashboardStatistics, WeekdayPattern, ModelMetricResponse
)
from ..services.canteen_service import CanteenService

router = APIRouter(prefix="/api", tags=["Canteen Operations"])

# --- 1. Meal Records Endpoints ---
@router.get("/records", response_model=List[MealRecordResponse])
def get_meal_records(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve operational meal records sorted chronologically descending."""
    return CanteenService.get_records(db, limit=limit, offset=offset)

@router.get("/records/{record_id}", response_model=MealRecordResponse)
def get_meal_record(record_id: int, db: Session = Depends(get_db)):
    """Retrieve a single operational meal record by ID."""
    record = CanteenService.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Meal record not found.")
    return record

@router.post("/records", response_model=MealRecordResponse, status_code=status.HTTP_201_CREATED)
def create_meal_record(record_in: MealRecordCreate, db: Session = Depends(get_db)):
    """Log a daily operational record with automatic day-of-week and waste derivation."""
    try:
        return CanteenService.create_record(db, record_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_record(record_id: int, db: Session = Depends(get_db)):
    """Delete a record by ID."""
    deleted = CanteenService.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meal record not found.")
    return None

# --- 2. Predictions & Recommendations Endpoints ---
@router.post("/predict", response_model=PredictionResponse)
def predict_demand_and_recommend(req: PredictionRequest, db: Session = Depends(get_db)):
    """Generate tomorrow's meal demand forecast, safety buffer, and waste reduction advice."""
    try:
        return CanteenService.predict_and_recommend(db, req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/predictions", response_model=List[PredictionResponse])
def get_historical_predictions(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve historical predictions with paired actual demand and prediction error."""
    return CanteenService.get_predictions(db, limit=limit)

# --- 3. Dashboard & Analytics Endpoints ---
@router.get("/dashboard/statistics", response_model=DashboardStatistics)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Retrieve real-time KPI metrics, waste totals, and model performance."""
    return CanteenService.get_dashboard_statistics(db)

@router.get("/analytics/weekday-patterns", response_model=List[WeekdayPattern])
def get_weekday_analytics(db: Session = Depends(get_db)):
    """Retrieve weekday meal consumption, preparation, and waste distribution."""
    return CanteenService.get_weekday_patterns(db)

@router.get("/model/performance", response_model=List[ModelMetricResponse])
def get_model_benchmarks(db: Session = Depends(get_db)):
    """Retrieve comparison metrics between Baseline and candidate ML models."""
    return CanteenService.get_model_metrics(db)
