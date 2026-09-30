from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from typing import Optional

from app.database.session import get_db
from app.models.database import Dataset
from app.core import dependencies
from app.services import customer_analytics, rfm_analysis, customer_segmentation

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/{dataset_id}")
def get_customer_analytics_route(
    dataset_id: int,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Retrieve customer summaries, repeat purchase rates, rankings, and at-risk accounts."""
    if current_dataset.status != "mapped":
        raise HTTPException(status_code=400, detail="Dataset must be configured and mapped first.")
        
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset file: {str(e)}")
        
    filters = {}
    if start_date: filters["start_date"] = start_date
    if end_date: filters["end_date"] = end_date
    if region: filters["region"] = region
    if category: filters["category"] = category
    
    return customer_analytics.get_customer_summary(df, filters=filters)

@router.get("/{dataset_id}/rfm")
def get_rfm_analysis_route(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Calculate RFM quintile scores and segment profiles for all customers."""
    if current_dataset.status != "mapped":
        raise HTTPException(status_code=400, detail="Dataset must be mapped first.")
        
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset file: {str(e)}")
        
    rfm_df = rfm_analysis.calculate_rfm_segments(df)
    summary = rfm_analysis.get_rfm_summary_stats(rfm_df)
    
    return {
        "summary": summary,
        "customer_segments": rfm_df.to_dict(orient="records")
    }

@router.post("/{dataset_id}/segmentation")
def run_kmeans_segmentation_route(
    dataset_id: int,
    n_clusters: Optional[int] = Query(4, ge=2, le=8),
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Perform K-Means clustering with PCA dimensionality reduction."""
    if current_dataset.status != "mapped":
        raise HTTPException(status_code=400, detail="Dataset must be mapped first.")
        
    try:
        df = pd.read_csv(current_dataset.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read dataset file: {str(e)}")
        
    evaluation = customer_segmentation.run_kmeans_evaluation(df)
    clusters_result = customer_segmentation.fit_customer_clusters(df, n_clusters=n_clusters)
    
    return {
        "evaluation": evaluation,
        "segmentation": clusters_result
    }
