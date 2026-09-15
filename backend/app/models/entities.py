from sqlalchemy import Column, Integer, Float, String, Date, DateTime, Boolean, Text, CheckConstraint
from datetime import datetime
from ..database.connection import Base

class MealRecord(Base):
    __tablename__ = "meal_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    day_of_week = Column(String(20), nullable=False)
    attendance = Column(Integer, nullable=False)
    meals_prepared = Column(Integer, nullable=False)
    meals_consumed = Column(Integer, nullable=False)
    waste = Column(Integer, nullable=False)
    is_holiday = Column(Integer, default=0)
    is_exam_day = Column(Integer, default=0)
    is_event_day = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("attendance >= 0", name="check_positive_attendance"),
        CheckConstraint("meals_prepared >= 0", name="check_positive_prepared"),
        CheckConstraint("meals_consumed >= 0", name="check_positive_consumed"),
        CheckConstraint("meals_consumed <= meals_prepared", name="check_consumed_le_prepared"),
        CheckConstraint("waste >= 0", name="check_positive_waste"),
    )

class PredictionRecord(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prediction_date = Column(Date, index=True, nullable=False)
    day_of_week = Column(String(20), nullable=False)
    expected_attendance = Column(Integer, nullable=False)
    predicted_demand = Column(Float, nullable=False)
    safety_buffer = Column(Integer, nullable=False)
    recommended_preparation = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)
    actual_demand = Column(Float, nullable=True)
    prediction_error = Column(Float, nullable=True)
    explanations = Column(Text, nullable=True)  # JSON serialized
    suggestions = Column(Text, nullable=True)   # JSON serialized
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_name = Column(String(50), nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    trained_at = Column(DateTime, default=datetime.utcnow)
