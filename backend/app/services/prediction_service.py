"""
Prediction service for business logic
"""
import numpy as np
from typing import Dict
from app.models.model_loader import model_manager
from app.services.feature_engineering import feature_engineer
from app.core.config import (
    SAFETY_STOCK_PERCENTAGE,
    CONFIDENCE_INTERVAL,
    LAG_PERIODS,
    ROLLING_WINDOWS
)


class PredictionService:
    """Handles prediction business logic"""
    
    @staticmethod
    def predict_sales(store: int, item: int, date: str) -> Dict:
        """
        Make sales prediction and calculate inventory recommendations
        
        Args:
            store: Store ID
            item: Item ID
            date: Prediction date in YYYY-MM-DD format
            
        Returns:
            Dictionary with prediction results
        """
        if not model_manager.is_ready():
            raise ValueError("Model or data not loaded")
        
        # Prepare features
        features, store_item_data = feature_engineer.prepare_features(
            store=store,
            item=item,
            date=date,
            all_data=model_manager.data,
            lag_periods=LAG_PERIODS,
            rolling_windows=ROLLING_WINDOWS
        )
        
        # Make prediction
        predicted_sales = model_manager.predict(features)
        
        # Calculate confidence interval
        std_error = store_item_data['sales'].std()
        confidence_lower = max(0, predicted_sales - CONFIDENCE_INTERVAL * std_error)
        confidence_upper = predicted_sales + CONFIDENCE_INTERVAL * std_error
        
        # Calculate recommended inventory (predicted + safety stock)
        safety_stock = predicted_sales * SAFETY_STOCK_PERCENTAGE
        recommended_inventory = int(np.ceil(predicted_sales + safety_stock))
        
        return {
            'predicted_sales': round(predicted_sales, 2),
            'recommended_inventory': recommended_inventory,
            'confidence_lower': round(confidence_lower, 2),
            'confidence_upper': round(confidence_upper, 2)
        }
    
    @staticmethod
    def get_analytics(store: int, item: int, days: int = 90) -> Dict:
        """Get historical analytics for a store-item combination"""
        if model_manager.data is None:
            raise ValueError("Data not loaded")
        
        # Filter data
        store_item_data = model_manager.data[
            (model_manager.data['store'] == store) & 
            (model_manager.data['item'] == item)
        ].copy()
        
        if len(store_item_data) == 0:
            raise ValueError(f"No data found for store {store}, item {item}")
        
        # Get recent data
        recent_data = store_item_data.tail(days)
        
        # Calculate statistics
        statistics = {
            'mean_sales': float(recent_data['sales'].mean()),
            'median_sales': float(recent_data['sales'].median()),
            'std_sales': float(recent_data['sales'].std()),
            'min_sales': float(recent_data['sales'].min()),
            'max_sales': float(recent_data['sales'].max()),
            'total_sales': float(recent_data['sales'].sum())
        }
        
        # Determine trend
        if len(recent_data) >= 30:
            first_half = recent_data.head(len(recent_data) // 2)['sales'].mean()
            second_half = recent_data.tail(len(recent_data) // 2)['sales'].mean()
            
            if second_half > first_half * 1.1:
                trend = "increasing"
            elif second_half < first_half * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Convert to list of dicts
        historical_data = recent_data[['date', 'sales']].to_dict('records')
        for record in historical_data:
            record['date'] = record['date'].strftime('%Y-%m-%d')
        
        return {
            'historical_data': historical_data,
            'statistics': statistics,
            'trend': trend
        }


# Global prediction service instance
prediction_service = PredictionService()
