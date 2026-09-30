from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import datetime

class DatasetResponse(BaseModel):
    id: int
    filename: str
    row_count: int
    col_count: int
    column_mappings: Dict[str, str]
    data_quality_score: float
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class ColumnMappingRequest(BaseModel):
    mappings: Dict[str, str]  # Standard name -> CSV column header name

class DataQualitySummary(BaseModel):
    rows: int
    cols: int
    missing_values: Dict[str, int]
    duplicate_rows: int
    date_range: Optional[List[str]] = None
    numeric_columns: List[str]
    categorical_columns: List[str]
    quality_score: float
    column_mappings: Dict[str, str]
    suggested_mappings: Dict[str, str]
    validation_errors: List[str]
    validation_warnings: List[str]
