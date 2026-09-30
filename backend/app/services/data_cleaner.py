import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Any

def clean_and_validate_dataset(
    file_path: str,
    mappings: Dict[str, str],
    output_cleaned_path: str
) -> Tuple[Dict[str, Any], bool]:
    """
    Cleans the uploaded file according to provided column mappings.
    Saves a cleaned CSV version to output_cleaned_path.
    
    Returns:
        (quality_report, success)
    """
    # Load raw dataset
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
        
    initial_rows = len(df)
    validation_errors = []
    validation_warnings = []
    
    # 1. Rename columns based on mappings
    # Invert mapping: user_column -> standard_column
    rename_dict = {user_col: std_col for std_col, user_col in mappings.items() if user_col in df.columns}
    df = df.rename(columns=rename_dict)
    
    # Filter columns to only contain standard columns (ignore extra unmapped ones)
    standard_columns = list(rename_dict.values())
    df = df[standard_columns]
    
    # 2. Check essential required columns
    required_fields = ["order_date", "sales", "quantity"]
    for field in required_fields:
        if field not in df.columns:
            validation_errors.append(f"Required field '{field}' is missing or unmapped.")
            
    if validation_errors:
        return {
            "rows": initial_rows,
            "cols": len(df.columns),
            "missing_values": {},
            "duplicate_rows": 0,
            "quality_score": 0.0,
            "validation_errors": validation_errors,
            "validation_warnings": [],
            "numeric_columns": [],
            "categorical_columns": []
        }, False

    # 3. Deduplicate
    duplicate_count = df.duplicated().sum()
    df = df.drop_duplicates()
    
    # 4. Handle types and values
    # Dates
    try:
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        null_dates = df["order_date"].isna().sum()
        if null_dates > 0:
            validation_warnings.append(f"Dropped {null_dates} rows due to invalid or missing order dates.")
            df = df.dropna(subset=["order_date"])
    except Exception as e:
        validation_errors.append(f"Failed to parse dates in 'order_date': {str(e)}")
        return {"validation_errors": validation_errors, "quality_score": 0.0}, False

    # Numeric fields: Sales & Quantity
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
    null_sales = df["sales"].isna().sum()
    if null_sales > 0:
        validation_warnings.append(f"Dropped {null_sales} rows due to invalid or missing sales figures.")
        df = df.dropna(subset=["sales"])
        
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    null_qty = df["quantity"].isna().sum()
    if null_qty > 0:
        validation_warnings.append(f"Dropped {null_qty} rows due to invalid or missing quantities.")
        df = df.dropna(subset=["quantity"])
        
    # Coerce unit price, profit, cost, discount if available
    for numeric_opt in ["unit_price", "discount", "cost", "profit"]:
        if numeric_opt in df.columns:
            df[numeric_opt] = pd.to_numeric(df[numeric_opt], errors="coerce").fillna(0.0)
            
    # Business logic fallback: If profit is not present, calculate standard profit
    if "profit" not in df.columns:
        if "cost" in df.columns:
            df["profit"] = df["sales"] - df["cost"]
        else:
            # Fallback assumption: 30% margin
            df["profit"] = df["sales"] * 0.3
            df["cost"] = df["sales"] * 0.7
            validation_warnings.append("Profit column is unmapped. Synthesized profit based on 30% margin fallback.")
            
    # Positive validation rules
    negative_sales_count = (df["sales"] < 0).sum()
    if negative_sales_count > 0:
        validation_warnings.append(f"Detected {negative_sales_count} rows with negative sales figures.")
        
    negative_qty_count = (df["quantity"] < 0).sum()
    if negative_qty_count > 0:
        validation_warnings.append(f"Detected {negative_qty_count} rows with negative quantity counts.")
        
    # 5. Handle optional categoricals (fill NA)
    categorical_fields = ["customer_name", "product_name", "category", "region"]
    for cat in categorical_fields:
        if cat in df.columns:
            df[cat] = df[cat].fillna("Unknown").astype(str).str.strip()
        else:
            # Insert default placeholder column
            if cat == "customer_name" and "customer_id" in df.columns:
                df["customer_name"] = df["customer_id"]
            elif cat == "category":
                df["category"] = "Uncategorized"
            elif cat == "region":
                df["region"] = "Global"
                
    # 6. Calculate Data Quality Score
    # Starting score = 100
    # Penalty:
    # - Percentage of rows dropped (max penalty 30 points)
    # - Percentage of missing cells across optional variables (max penalty 20 points)
    # - Negative sales/quantities (max penalty 20 points)
    # - Duplicate ratio (max penalty 10 points)
    # - Missing critical metadata like product names or customer IDs (max penalty 20 points)
    
    rows_dropped = initial_rows - len(df)
    drop_pct = (rows_dropped / initial_rows) if initial_rows > 0 else 0
    drop_penalty = min(30.0, drop_pct * 100.0)
    
    neg_pct = ((negative_sales_count + negative_qty_count) / len(df)) if len(df) > 0 else 0
    neg_penalty = min(20.0, neg_pct * 100.0)
    
    dup_pct = (duplicate_count / initial_rows) if initial_rows > 0 else 0
    dup_penalty = min(10.0, dup_pct * 100.0)
    
    # Calculate missing values count in remaining data
    missing_counts = df.isna().sum().to_dict()
    total_missing = sum(missing_counts.values())
    total_cells = df.size
    missing_pct = (total_missing / total_cells) if total_cells > 0 else 0
    missing_penalty = min(20.0, missing_pct * 100.0)
    
    meta_penalty = 0.0
    if "customer_id" not in df.columns:
        meta_penalty += 10.0
        validation_warnings.append("No Customer ID mapping provided. Customer metrics and RFM will be disabled.")
    if "product_name" not in df.columns:
        meta_penalty += 10.0
        validation_warnings.append("No Product Name mapping provided. Product performance metrics will be disabled.")
        
    quality_score = max(0.0, round(100.0 - drop_penalty - neg_penalty - dup_penalty - missing_penalty - meta_penalty, 2))
    
    # 7. Collect metadata
    numeric_columns = list(df.select_dtypes(include=[np.number]).columns)
    categorical_columns = [col for col in df.columns if col not in numeric_columns and col != "order_date"]
    
    date_range = None
    if len(df) > 0:
        date_range = [
            df["order_date"].min().strftime("%Y-%m-%d"),
            df["order_date"].max().strftime("%Y-%m-%d")
        ]
        
    # Create final cleaned directory and output
    os.makedirs(os.path.dirname(output_cleaned_path), exist_ok=True)
    df.to_csv(output_cleaned_path, index=False)
    
    quality_report = {
        "rows": len(df),
        "cols": len(df.columns),
        "missing_values": {str(k): int(v) for k, v in missing_counts.items()},
        "duplicate_rows": int(duplicate_count),
        "date_range": date_range,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "quality_score": float(quality_score),
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings
    }
    
    return quality_report, True
