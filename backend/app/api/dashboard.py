from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import pandas as pd
from typing import Optional, List

from app.database.session import get_db
from app.models.database import Dataset, User
from app.core import dependencies
from app.services import sales_analytics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/{dataset_id}")
def get_dashboard_data(
    dataset_id: int,
    start_date: Optional[str] = Query(None, description="Start date filter YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date filter YYYY-MM-DD"),
    region: Optional[str] = Query(None, description="Region filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """
    Get consolidated dashboard metrics (KPIs, category breakdown, regional breakdown, trend lines)
    for a specific dataset, applying optional filters.
    """
    # Verify dataset is clean and mapped
    if current_dataset.status != "mapped":
        return {
            "status": "error",
            "message": "Dataset must be configured and column-mapped before running analysis."
        }
        
    # Read the cleaned dataset file
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load dataset file: {str(e)}"
        }
        
    filters = {}
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
    if region:
        filters["region"] = region
    if category:
        filters["category"] = category
        
    results = sales_analytics.get_sales_overview(df, filters=filters)
    return results
