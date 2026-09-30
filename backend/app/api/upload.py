from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import os
import shutil
import json

from app.database.session import get_db
from app.models.database import User, Dataset
from app.core import dependencies, config
from app.schemas.dataset import DatasetResponse, ColumnMappingRequest, DataQualitySummary
from app.services import data_loader, data_cleaner

router = APIRouter(prefix="/datasets", tags=["Datasets"])

@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """
    Step 1: Upload CSV/XLSX file.
    Saves file raw on disk, analyzes headers, and returns suggested mappings.
    """
    # Validate extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a CSV or Excel (.xlsx/.xls) file."
        )

    # Setup directories
    user_raw_dir = os.path.join(config.settings.UPLOAD_DIR, f"user_{current_user.id}", "raw")
    os.makedirs(user_raw_dir, exist_ok=True)
    
    file_path = os.path.join(user_raw_dir, file.filename)
    
    # Save raw file
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
        
    # Analyze raw file
    try:
        meta = data_loader.load_file_metadata(file_path)
    except Exception as e:
        # Cleanup file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing raw file. Ensure file is not malformed: {str(e)}"
        )
        
    # Create dataset record
    new_dataset = Dataset(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        row_count=meta["row_count"],
        col_count=meta["col_count"],
        column_mappings=json.dumps(meta["suggested_mappings"]),
        data_quality_score=0.0,
        status="uploaded"
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    
    # Custom load of mappings dict for response compatibility
    response_data = {
        "id": new_dataset.id,
        "filename": new_dataset.filename,
        "row_count": new_dataset.row_count,
        "col_count": new_dataset.col_count,
        "column_mappings": meta["suggested_mappings"],
        "data_quality_score": new_dataset.data_quality_score,
        "status": new_dataset.status,
        "created_at": new_dataset.created_at
    }
    
    return response_data

@router.post("/{dataset_id}/map", response_model=DataQualitySummary)
def map_columns(
    dataset_id: int,
    mapping_req: ColumnMappingRequest,
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """
    Step 2: Confirm column mappings.
    Cleans data, drops duplicates/nulls, scores quality, saves cleaned CSV, and updates dataset.
    """
    user_id = current_dataset.user_id
    user_cleaned_dir = os.path.join(config.settings.UPLOAD_DIR, f"user_{user_id}", "cleaned")
    os.makedirs(user_cleaned_dir, exist_ok=True)
    
    cleaned_file_path = os.path.join(user_cleaned_dir, current_dataset.filename)
    
    # Run data cleaning
    quality_report, success = data_cleaner.clean_and_validate_dataset(
        file_path=current_dataset.file_path,
        mappings=mapping_req.mappings,
        output_cleaned_path=cleaned_file_path
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation failed: {', '.join(quality_report.get('validation_errors', []))}"
        )
        
    # Update dataset record
    current_dataset.column_mappings = json.dumps(mapping_req.mappings)
    current_dataset.row_count = quality_report["rows"]
    current_dataset.col_count = quality_report["cols"]
    current_dataset.data_quality_score = quality_report["quality_score"]
    current_dataset.file_path = cleaned_file_path  # Point to cleaned file path from now on
    current_dataset.status = "mapped"
    
    db.commit()
    db.refresh(current_dataset)
    
    quality_report["column_mappings"] = mapping_req.mappings
    quality_report["suggested_mappings"] = mapping_req.mappings
    
    return quality_report

@router.get("", response_model=list[DatasetResponse])
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_user)
):
    """List all dataset profiles owned by the current user."""
    datasets = db.query(Dataset).filter(Dataset.user_id == current_user.id).all()
    
    # Format JSON mappings for responses
    response_list = []
    for d in datasets:
        try:
            mappings_dict = json.loads(d.column_mappings)
        except:
            mappings_dict = {}
        response_list.append({
            "id": d.id,
            "filename": d.filename,
            "row_count": d.row_count,
            "col_count": d.col_count,
            "column_mappings": mappings_dict,
            "data_quality_score": d.data_quality_score,
            "status": d.status,
            "created_at": d.created_at
        })
    return response_list

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Retrieve metadata details for a specific dataset."""
    try:
        mappings_dict = json.loads(current_dataset.column_mappings)
    except:
        mappings_dict = {}
        
    return {
        "id": current_dataset.id,
        "filename": current_dataset.filename,
        "row_count": current_dataset.row_count,
        "col_count": current_dataset.col_count,
        "column_mappings": mappings_dict,
        "data_quality_score": current_dataset.data_quality_score,
        "status": current_dataset.status,
        "created_at": current_dataset.created_at
    }

@router.delete("/{dataset_id}")
def delete_dataset(
    db: Session = Depends(get_db),
    current_dataset: Dataset = Depends(dependencies.get_user_dataset)
):
    """Delete dataset file on disk and remove metadata from database."""
    # Delete clean and raw files if exist
    try:
        raw_path = current_dataset.file_path
        # Cleaned path might be same or different
        user_id = current_dataset.user_id
        raw_dir = os.path.join(config.settings.UPLOAD_DIR, f"user_{user_id}", "raw")
        cleaned_dir = os.path.join(config.settings.UPLOAD_DIR, f"user_{user_id}", "cleaned")
        
        raw_file = os.path.join(raw_dir, current_dataset.filename)
        cleaned_file = os.path.join(cleaned_dir, current_dataset.filename)
        
        for p in [raw_file, cleaned_file]:
            if os.path.exists(p):
                os.remove(p)
    except Exception as e:
        # Non-critical warning, log and proceed with DB delete
        print(f"Warning: Failed to delete physical dataset files: {str(e)}")
        
    db.delete(current_dataset)
    db.commit()
    return {"status": "success", "message": "Dataset and all associated records deleted."}
