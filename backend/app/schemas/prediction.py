"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request model for single prediction"""
    store: int = Field(..., ge=1, le=10, description="Store ID (1-10)")
    item: int = Field(..., ge=1, le=50, description="Item ID (1-50)")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class BatchPredictionRequest(BaseModel):
    """Request model for batch predictions"""
    predictions: List[PredictionRequest]


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    store: int
    item: int
    date: str
    predicted_sales: float
    recommended_inventory: int
    confidence_lower: float
    confidence_upper: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    data_loaded: bool
    timestamp: str


class ModelInfoResponse(BaseModel):
    """Model information response"""
    name: str
    type: str
    rmse: float
    mae: float
    r2: float
    mape: float
    loaded: bool


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    store: int
    item: int
    historical_data: List[Dict[str, Any]]
    statistics: Dict[str, float]
    trend: str


class ForecastResponse(BaseModel):
    """Forecast response"""
    store: int
    item: int
    forecast_days: int
    predictions: List[PredictionResponse]
