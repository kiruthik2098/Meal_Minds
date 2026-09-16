from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Literal

MealTypeEnum = Literal["breakfast", "lunch", "snacks", "dinner"]

# 1. Meal Record Schemas
class MealRecordCreate(BaseModel):
    date: date
    meal_type: MealTypeEnum = "lunch"
    attendance: int = Field(..., ge=0, description="Number of students on campus")
    meals_prepared: int = Field(..., ge=0, description="Total meals prepared by staff")
    meals_consumed: int = Field(..., ge=0, description="Total meals consumed by students")
    is_holiday: Optional[int] = Field(0, ge=0, le=1)
    is_exam_day: Optional[int] = Field(0, ge=0, le=1)
    is_event_day: Optional[int] = Field(0, ge=0, le=1)

    @model_validator(mode="after")
    def validate_consumption(self):
        if self.meals_consumed > self.meals_prepared:
            raise ValueError(
                f"Physical impossibility: meals_consumed ({self.meals_consumed}) cannot exceed meals_prepared ({self.meals_prepared})."
            )
        return self

class MealRecordUpdate(BaseModel):
    date: Optional[date] = None
    meal_type: Optional[MealTypeEnum] = None
    attendance: Optional[int] = Field(None, ge=0)
    meals_prepared: Optional[int] = Field(None, ge=0)
    meals_consumed: Optional[int] = Field(None, ge=0)
    is_holiday: Optional[int] = Field(None, ge=0, le=1)
    is_exam_day: Optional[int] = Field(None, ge=0, le=1)
    is_event_day: Optional[int] = Field(None, ge=0, le=1)

class MealRecordResponse(BaseModel):
    id: int
    date: date
    meal_type: str
    day_of_week: str
    attendance: int
    meals_prepared: int
    meals_consumed: int
    waste: int
    is_holiday: int
    is_exam_day: int
    is_event_day: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

# 2. Prediction Schemas
class PredictionRequest(BaseModel):
    date: date
    meal_type: Optional[MealTypeEnum] = "lunch"
    expected_attendance: int = Field(..., ge=1, le=2000, description="Expected student attendance count")
    is_holiday: Optional[int] = Field(0, ge=0, le=1)
    is_exam_day: Optional[int] = Field(0, ge=0, le=1)
    is_event_day: Optional[int] = Field(0, ge=0, le=1)

class ExplanationItem(BaseModel):
    type: str
    icon: str
    text: str

class SuggestionItem(BaseModel):
    level: str
    title: str
    message: str

class PredictionResponse(BaseModel):
    id: Optional[int] = None
    date: date
    meal_type: str = "lunch"
    day_of_week: str
    expected_attendance: int
    predicted_demand: float
    safety_buffer: int
    recommended_preparation: int
    model_name: str
    model_mae: float
    explanations: List[ExplanationItem]
    suggestions: List[SuggestionItem]
    actual_demand: Optional[float] = None
    prediction_error: Optional[float] = None

# 3. Dashboard and Analytics Schemas
class DashboardStatistics(BaseModel):
    total_records: int
    total_meals_prepared: int
    total_meals_consumed: int
    total_waste: int
    overall_waste_percentage: float
    avg_daily_attendance: float
    avg_daily_demand: float
    avg_daily_waste: float
    estimated_cost_wasted: float  # Assumption: INR 45 per meal
    active_model_name: str
    active_model_mae: float
    baseline_mae: float
    mae_improvement_pct: float

class WeekdayPattern(BaseModel):
    day_of_week: str
    avg_attendance: float
    avg_prepared: float
    avg_consumed: float
    avg_waste: float
    waste_percentage: float

class ModelMetricResponse(BaseModel):
    id: int
    model_name: str
    mae: float
    rmse: float
    r2: float
    is_active: bool
    trained_at: datetime

    class Config:
        from_attributes = True
