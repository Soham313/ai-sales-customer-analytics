import pandas as pd
import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def detect_sales_anomalies(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detect transactions and date-level aggregates that contain statistical anomalies.
    Uses scikit-learn Isolation Forest on transaction-level features (sales, quantity, profit).
    """
    if len(df) < 10:
        return {
            "anomaly_count": 0,
            "anomaly_percentage": 0.0,
            "anomalous_transactions": [],
            "anomalous_dates": []
        }
        
    df_copy = df.copy()
    
    # 1. Transaction-level anomaly detection
    # Features: Sales, Quantity, Profit, and Discount (if available)
    feature_cols = ["sales", "quantity", "profit"]
    if "discount" in df_copy.columns:
        feature_cols.append("discount")
        
    features = df_copy[feature_cols].copy()
    
    # Standardize features
    scaler = StandardScaler()
    scaled_feats = scaler.fit_transform(features)
    
    # Fit Isolation Forest (contamination is the proportion of outliers in the data)
    # Contamination set to 1.5% (approx 15 anomalies per 1000 rows)
    iso_forest = IsolationForest(contamination=0.015, random_state=42)
    df_copy["anomaly_label"] = iso_forest.fit_predict(scaled_feats)
    df_copy["anomaly_score"] = iso_forest.decision_function(scaled_feats) # Lower = more anomalous
    
    # Filter anomalies (label == -1)
    anomalies_df = df_copy[df_copy["anomaly_label"] == -1].copy()
    
    # Sort anomalies so the most extreme ones are first (lowest anomaly score)
    anomalies_df = anomalies_df.sort_values(by="anomaly_score")
    
    anomaly_count = len(anomalies_df)
    anomaly_pct = (anomaly_count / len(df_copy)) * 100.0
    
    # Format anomalies for front-end rendering
    cols_to_return = ["order_id", "order_date", "customer_name", "product_name", "category", "region", "sales", "quantity", "profit", "anomaly_score"]
    if "discount" in df_copy.columns:
        cols_to_return.append("discount")
        
    # Ensure all columns are present before slicing
    existing_cols = [c for c in cols_to_return if c in anomalies_df.columns]
    
    # Get top 20 most extreme anomalies
    anomalous_transactions = anomalies_df[existing_cols].head(25).round(2)
    # Format date
    if "order_date" in anomalous_transactions.columns:
        # Check if already datetime or string
        if pd.api.types.is_datetime64_any_dtype(anomalous_transactions["order_date"]):
            anomalous_transactions["order_date"] = anomalous_transactions["order_date"].dt.strftime("%Y-%m-%d")
            
    anomalous_tx_list = anomalous_transactions.to_dict(orient="records")
    
    # 2. Date-level anomaly detection (looking at temporal drops/spikes)
    # Group by date to find days with abnormal volume/sales
    daily_aggregates = df_copy.groupby("order_date").agg({
        "sales": "sum",
        "order_id": "count"
    }).rename(columns={"order_id": "order_count"}).reset_index()
    
    if len(daily_aggregates) >= 10:
        daily_scaler = StandardScaler()
        daily_scaled = daily_scaler.fit_transform(daily_aggregates[["sales", "order_count"]])
        
        daily_iso = IsolationForest(contamination=0.03, random_state=42) # 3% contamination for dates
        daily_aggregates["anomaly_label"] = daily_iso.fit_predict(daily_scaled)
        
        anomalous_dates_df = daily_aggregates[daily_aggregates["anomaly_label"] == -1].copy()
        
        # Calculate standard deviation/median deviation to explain anomalies
        median_sales = float(daily_aggregates["sales"].median())
        
        anomalous_dates_list = []
        for idx, row in anomalous_dates_df.iterrows():
            date_str = row["order_date"]
            if not isinstance(date_str, str):
                date_str = date_str.strftime("%Y-%m-%d")
                
            val_sales = float(row["sales"])
            dev_pct = ((val_sales - median_sales) / median_sales * 100.0) if median_sales > 0 else 0.0
            
            anomalous_dates_list.append({
                "date": date_str,
                "sales": round(val_sales, 2),
                "order_count": int(row["order_count"]),
                "deviation_percentage": round(dev_pct, 2)
            })
            
        # Sort anomalous dates chronologically
        anomalous_dates_list.sort(key=lambda x: x["date"])
    else:
        anomalous_dates_list = []
        
    return {
        "anomaly_count": int(anomaly_count),
        "anomaly_percentage": round(float(anomaly_pct), 2),
        "anomalous_transactions": anomalous_tx_list,
        "anomalous_dates": anomalous_dates_list
    }
