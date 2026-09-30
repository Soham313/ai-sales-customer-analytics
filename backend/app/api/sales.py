from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from typing import Optional

from app.database.session import get_db
from app.models.database import Dataset
from app.core import dependencies
from app.services import sales_analytics

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.get("/{dataset_id}")
def get_sales_growth_analytics(
    dataset_id: int,
    start_date: str = Query(..., description="Start date of analysis range YYYY-MM-DD"),
    end_date: str = Query(..., description="End date of analysis range YYYY-MM-DD"),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """
    Detailed sales performance. Compares the selected date range vs the
    equivalent previous duration (e.g. QoQ or YoY depending on delta).
    """
    if current_dataset.status != "mapped":
        raise HTTPException(
            status_code=400,
            detail="Dataset must be configured and mapped first."
        )
        
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset: {str(e)}")
        
    filters = {}
    if region:
        filters["region"] = region
    if category:
        filters["category"] = category
        
    try:
        results = sales_analytics.get_sales_growth(
            df=df,
            start_date=start_date,
            end_date=end_date,
            filters=filters
        )
        return results
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error running comparison: {str(e)}"
        )
