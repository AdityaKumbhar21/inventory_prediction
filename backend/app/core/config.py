"""
Configuration settings for the application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Model settings
MODEL_DIR = BASE_DIR / "models"
MODEL_FILE = "xgboost_model.pkl"
MODEL_PATH = MODEL_DIR / MODEL_FILE

# Data settings
DATA_DIR = BASE_DIR / "data" / "processed"
DATA_FILE = "processed_kaggle_sales_data.csv"
DATA_PATH = DATA_DIR / DATA_FILE

# API settings
API_TITLE = "Inventory Prediction API"
API_DESCRIPTION = "XGBoost-based ML API for retail inventory demand forecasting"
API_VERSION = "1.0.0"

# CORS settings
# Specific origins for exact matching
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
    "https://inventory-prediction.vercel.app",
]

# Regex pattern for Vercel preview deployments (e.g., https://*.vercel.app)
CORS_ORIGIN_REGEX = r"https://.*\.vercel\.app"

# Business logic constants
SAFETY_STOCK_PERCENTAGE = 0.2  # 20% safety stock
CONFIDENCE_INTERVAL = 1.96  # 95% confidence interval

# Store and Item ranges
MIN_STORE_ID = 1
MAX_STORE_ID = 10
MIN_ITEM_ID = 1
MAX_ITEM_ID = 50

# Forecasting limits
MAX_FORECAST_DAYS = 30
MAX_BATCH_SIZE = 100

# Feature engineering parameters
LAG_PERIODS = [1, 3, 7, 14, 30, 60, 90]
ROLLING_WINDOWS = [7, 14, 30, 60, 90]
