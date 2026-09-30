from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from typing import Optional

from app.database.session import get_db
from app.models.database import Dataset
from app.core import dependencies
from app.services import forecasting_service

router = APIRouter(prefix="/forecast", tags=["Forecasting"])

@router.post("/{dataset_id}")
def generate_forecast_route(
    dataset_id: int,
    horizon_days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Generate time-series sales predictions for 30, 60, or 90 days with confidence intervals."""
    if current_dataset.status != "mapped":
        raise HTTPException(status_code=400, detail="Dataset must be mapped first.")
        
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset file: {str(e)}")
        
    forecast_data = forecasting_service.generate_sales_forecast(df, horizon_days=horizon_days)
    return forecast_data
