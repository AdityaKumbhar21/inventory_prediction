"""
Model loading and management
"""
import joblib
from pathlib import Path
from typing import Optional
import pandas as pd


class ModelManager:
    """Manages XGBoost model loading and predictions"""
    
    def __init__(self):
        self.model = None
        self.data = None
        
    def load_model(self, model_path: Path) -> bool:
        """Load XGBoost model from disk"""
        try:
            if model_path.exists():
                self.model = joblib.load(model_path)
                print(f"✓ XGBoost model loaded from {model_path}")
                return True
            else:
                print(f"✗ Model file not found: {model_path}")
                return False
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            return False
    
    def load_data(self, data_path: Path) -> bool:
        """Load processed training data"""
        try:
            if data_path.exists():
                self.data = pd.read_csv(data_path)
                self.data['date'] = pd.to_datetime(self.data['date'])
                print(f"✓ Data loaded: {len(self.data)} records")
                return True
            else:
                print(f"✗ Data file not found: {data_path}")
                return False
        except Exception as e:
            print(f"✗ Failed to load data: {e}")
            return False
    
    def predict(self, features: pd.DataFrame) -> float:
        """Make prediction using XGBoost model"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        prediction = self.model.predict(features)[0]
        return max(0, float(prediction))  # Ensure non-negative
    
    def is_ready(self) -> bool:
        """Check if model and data are loaded"""
        return self.model is not None and self.data is not None


# Global model manager instance
model_manager = ModelManager()
