from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.database.session import get_db
from app.models.database import Dataset
from app.core import dependencies
from app.services import anomaly_detection

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

@router.get("/{dataset_id}")
def get_anomalies_route(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Detect outlier transactions and abnormal daily sales using Isolation Forest."""
    if current_dataset.status != "mapped":
        raise HTTPException(status_code=400, detail="Dataset must be mapped first.")
        
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset file: {str(e)}")
        
    anomalies_result = anomaly_detection.detect_sales_anomalies(df)
    return anomalies_result
