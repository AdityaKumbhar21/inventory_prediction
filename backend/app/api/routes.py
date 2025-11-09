"""
API route handlers
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List
from datetime import timedelta

from app.schemas.prediction import (
    PredictionRequest,
    BatchPredictionRequest,
    PredictionResponse,
    HealthResponse,
    ModelInfoResponse,
    AnalyticsResponse,
    ForecastResponse
)
from app.services.prediction_service import prediction_service
from app.models.model_loader import model_manager
from app.core.config import (
    MIN_STORE_ID,
    MAX_STORE_ID,
    MIN_ITEM_ID,
    MAX_ITEM_ID,
    MAX_FORECAST_DAYS,
    MAX_BATCH_SIZE
)
from datetime import datetime

router = APIRouter()


@router.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "Inventory Prediction API",
        "version": "1.0.0",
        "model": "XGBoost",
        "docs": "/docs",
        "health": "/health"
    }


@router.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model_manager.model is not None,
        data_loaded=model_manager.data is not None,
        timestamp=datetime.now().isoformat()
    )


@router.get("/model", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """Get XGBoost model information and performance metrics"""
    return ModelInfoResponse(
        name="xgboost",
        type="XGBoost Regressor",
        rmse=10.23,
        mae=7.45,
        r2=0.884,
        mape=14.68,
        loaded=model_manager.model is not None
    )


@router.get("/stores", tags=["Data"])
async def list_stores():
    """List all available stores"""
    return {
        "stores": list(range(MIN_STORE_ID, MAX_STORE_ID + 1)),
        "count": MAX_STORE_ID - MIN_STORE_ID + 1
    }


@router.get("/items", tags=["Data"])
async def list_items():
    """List all available items"""
    return {
        "items": list(range(MIN_ITEM_ID, MAX_ITEM_ID + 1)),
        "count": MAX_ITEM_ID - MIN_ITEM_ID + 1
    }


@router.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_inventory(request: PredictionRequest):
    """
    Make a single inventory prediction
    
    Returns:
    - Predicted sales
    - Recommended inventory (sales + safety stock)
    - Confidence intervals (95%)
    """
    try:
        result = prediction_service.predict_sales(
            store=request.store,
            item=request.item,
            date=request.date
        )
        
        return PredictionResponse(
            store=request.store,
            item=request.item,
            date=request.date,
            **result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch-predict", response_model=List[PredictionResponse], tags=["Predictions"])
async def batch_predict(request: BatchPredictionRequest):
    """Make batch predictions for multiple store-item-date combinations"""
    if len(request.predictions) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size too large. Maximum {MAX_BATCH_SIZE} predictions per request."
        )
    
    results = []
    for pred_req in request.predictions:
        try:
            result = await predict_inventory(pred_req)
            results.append(result)
        except Exception as e:
            print(f"Error in batch prediction: {e}")
            continue
    
    return results


@router.get("/analytics/{store}/{item}", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_analytics(
    store: int = Path(..., ge=MIN_STORE_ID, le=MAX_STORE_ID),
    item: int = Path(..., ge=MIN_ITEM_ID, le=MAX_ITEM_ID),
    days: int = Query(90, ge=1, le=365, description="Number of days of history")
):
    """Get historical analytics for a store-item combination"""
    try:
        result = prediction_service.get_analytics(store, item, days)
        
        return AnalyticsResponse(
            store=store,
            item=item,
            **result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/forecast/{store}/{item}", response_model=ForecastResponse, tags=["Predictions"])
async def forecast_next_days(
    store: int = Path(..., ge=MIN_STORE_ID, le=MAX_STORE_ID),
    item: int = Path(..., ge=MIN_ITEM_ID, le=MAX_ITEM_ID),
    days: int = Query(7, ge=1, le=MAX_FORECAST_DAYS, description="Number of days to forecast"),
    start_date: str = Query(None, description="Start date for forecast (YYYY-MM-DD)")
):
    """Forecast sales for the next N days starting from a specific date"""
    if model_manager.data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    # Use provided start_date or default to last date in data
    if start_date:
        from datetime import datetime as dt
        try:
            base_date = dt.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        base_date = model_manager.data['date'].max()
    
    # Generate predictions for next N days
    predictions = []
    for i in range(1, days + 1):
        forecast_date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        
        request = PredictionRequest(
            store=store,
            item=item,
            date=forecast_date
        )
        
        try:
            pred = await predict_inventory(request)
            predictions.append(pred)
        except Exception as e:
            print(f"Forecast error for {forecast_date}: {e}")
            continue
    
    return ForecastResponse(
        store=store,
        item=item,
        forecast_days=days,
        predictions=predictions
    )
