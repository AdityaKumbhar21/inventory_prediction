# Inventory Prediction Backend

XGBoost-based FastAPI backend for inventory demand forecasting.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── api/
│   │   └── routes.py           # API endpoints
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── models/
│   │   └── model_loader.py     # Model management
│   ├── schemas/
│   │   └── prediction.py       # Pydantic models
│   └── services/
│       ├── feature_engineering.py  # Feature creation
│       └── prediction_service.py   # Business logic
├── run.py                      # Run script
└── main.py                     # Legacy (deprecated)
```

## 🎯 Features

- ✅ **Single Model**: XGBoost only (no bloat)
- ✅ **Separation of Concerns**: Clean architecture
- ✅ **Type Safety**: Pydantic schemas
- ✅ **Feature Engineering**: Automated feature creation
- ✅ **Business Logic**: Separated from API layer

## 🚀 Quick Start

### Option 1: Using new structure (recommended)
```bash
cd backend
python run.py
```

### Option 2: Using Uvicorn directly
```bash
cd backend
uvicorn app.main:app --reload
```

## 📡 API Endpoints

### General
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /model` - Model info

### Data
- `GET /stores` - List stores (1-10)
- `GET /items` - List items (1-50)

### Predictions
- `POST /predict` - Single prediction
- `POST /batch-predict` - Batch predictions
- `GET /forecast/{store}/{item}` - Multi-day forecast

### Analytics
- `GET /analytics/{store}/{item}` - Historical analytics

## 📊 Model Performance

**XGBoost Metrics:**
- RMSE: 10.23
- MAE: 7.45
- R²: 0.884 (88.4% accuracy)
- MAPE: 14.68%

## 🔧 Configuration

Edit `app/core/config.py` to change:
- Model paths
- Data paths
- CORS origins
- Business rules (safety stock %, confidence intervals)
- Feature engineering parameters

## 📝 Example Request

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "item": 1,
    "date": "2025-11-15"
  }'
```

## 🎓 Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Services are injected, not created
3. **Configuration Over Code**: Settings in `config.py`
4. **Type Safety**: Pydantic schemas for validation
5. **Clean Architecture**: API → Service → Model layers

## 🔄 Migration from Old Structure

The old `main.py` is deprecated. Use the new structure:

**Old:**
```python
# backend/main.py (520 lines, everything mixed)
```

**New:**
```python
# backend/app/main.py (50 lines, clean)
# backend/app/api/routes.py (API layer)
# backend/app/services/ (Business logic)
# backend/app/models/ (Model management)
```

## 📦 Dependencies

Only essential packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `xgboost` - ML model
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `joblib` - Model persistence

Removed:
- ❌ `lightgbm` - Not used
- ❌ `scipy` - Not used
- ❌ Random Forest, Neural Network models

## 🎯 Next Steps

1. Run `python run.py` to start server
2. Visit http://localhost:8000/docs for API docs
3. Test with `/predict` endpoint
4. Deploy to Render using this structure
