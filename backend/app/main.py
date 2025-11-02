"""
FastAPI Application - Main Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
    MODEL_PATH,
    DATA_PATH
)
from app.api.routes import router
from app.models.model_loader import model_manager


# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# ==================== Startup & Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Load model and data on startup"""
    print("=" * 60)
    print("Starting Inventory Prediction API...")
    print("=" * 60)
    
    # Load XGBoost model
    print("\n[1/2] Loading XGBoost model...")
    model_loaded = model_manager.load_model(MODEL_PATH)
    
    # Load processed data
    print("\n[2/2] Loading processed data...")
    data_loaded = model_manager.load_data(DATA_PATH)
    
    print("\n" + "=" * 60)
    if model_loaded and data_loaded:
        print("✓ API Ready!")
    else:
        print("⚠ API started with warnings (check logs above)")
    print("=" * 60)
    print(f"📖 API Documentation: http://localhost:8000/docs")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n" + "=" * 60)
    print("Shutting down API...")
    print("=" * 60)
