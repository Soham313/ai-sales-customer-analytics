import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from app.services.sales_analytics import apply_filters

def get_customer_summary(df: pd.DataFrame, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Calculate overall customer-level statistics and repeat behaviors."""
    df["order_date"] = pd.to_datetime(df["order_date"])
    filtered_df = apply_filters(df, filters)
    
    if filtered_df.empty:
        return {
            "total_customers": 0,
            "new_customers": 0,
            "returning_customers": 0,
            "avg_customer_revenue": 0.0,
            "avg_order_frequency": 0.0,
            "repeat_purchase_rate": 0.0,
            "top_spent_customers": [],
            "top_frequent_customers": []
        }
        
    # Unique customers
    total_cust = filtered_df["customer_id"].nunique()
    
    # Customer groupings
    cust_aggregates = filtered_df.groupby("customer_id").agg({
        "order_date": ["min", "max", "count"],
        "sales": "sum"
    })
    cust_aggregates.columns = ["first_purchase", "last_purchase", "order_count", "total_spent"]
    cust_aggregates = cust_aggregates.reset_index()
    
    # Identify new customers in this period (first purchase fell in this period)
    # If no date filter, all customers are technically "new" relative to the beginning
    # Let's define new customers as those whose global first purchase date is within the filter date range
    global_first_purchase = df.groupby("customer_id")["order_date"].min().to_dict()
    
    start_date = None
    if filters and "start_date" in filters and filters["start_date"]:
        start_date = pd.to_datetime(filters["start_date"])
        
    new_cust_count = 0
    for cust_id, first_date in global_first_purchase.items():
        # Check if customer purchased in filtered set
        if cust_id in cust_aggregates["customer_id"].values:
            if start_date is None or first_date >= start_date:
                new_cust_count += 1
                
    returning_cust_count = max(0, total_cust - new_cust_count)
    
    # Value summaries
    avg_cust_rev = float(filtered_df["sales"].sum() / total_cust) if total_cust > 0 else 0.0
    
    # Order column matching
    order_col = "order_id" if "order_id" in filtered_df.columns else "index"
    total_orders = filtered_df[order_col].nunique() if order_col in filtered_df.columns else len(filtered_df)
    avg_freq = float(total_orders / total_cust) if total_cust > 0 else 0.0
    
    # Repeat purchase rate (percentage of customers with > 1 order in historical dataset)
    global_counts = df.groupby("customer_id")["order_id"].nunique() if "order_id" in df.columns else df.groupby("customer_id").size()
    repeat_customers = (global_counts > 1).sum()
    total_global_customers = len(global_counts)
    repeat_purchase_rate = (repeat_customers / total_global_customers * 100) if total_global_customers > 0 else 0.0
    
    # Rank spent
    customer_names = filtered_df.groupby("customer_id")["customer_name"].first().to_dict()
    
    top_spent = cust_aggregates.sort_values(by="total_spent", ascending=False).head(10).copy()
    top_spent["customer_name"] = top_spent["customer_id"].map(customer_names)
    top_spent["last_purchase"] = top_spent["last_purchase"].dt.strftime("%Y-%m-%d")
    top_spent["first_purchase"] = top_spent["first_purchase"].dt.strftime("%Y-%m-%d")
    top_spent_list = top_spent.round(2).to_dict(orient="records")
    
    # Rank frequency
    top_freq = cust_aggregates.sort_values(by="order_count", ascending=False).head(10).copy()
    top_freq["customer_name"] = top_freq["customer_id"].map(customer_names)
    top_freq["last_purchase"] = top_freq["last_purchase"].dt.strftime("%Y-%m-%d")
    top_freq["first_purchase"] = top_freq["first_purchase"].dt.strftime("%Y-%m-%d")
    top_frequent_list = top_freq.round(2).to_dict(orient="records")
    
    # At risk: Customers with declining activity
    # Find customers who haven't ordered in the last 90 days of the dataset's span
    max_dataset_date = df["order_date"].max()
    at_risk_date_boundary = max_dataset_date - pd.Timedelta(days=90)
    
    all_cust_agg = df.groupby("customer_id").agg({
        "order_date": "max",
        "sales": "sum",
        "order_id": "count"
    }).rename(columns={"order_date": "last_purchase", "order_id": "total_orders", "sales": "total_spent"}).reset_index()
    
    at_risk_df = all_cust_agg[all_cust_agg["last_purchase"] < at_risk_date_boundary].copy()
    at_risk_df["days_inactive"] = (max_dataset_date - at_risk_df["last_purchase"]).dt.days
    
    global_names = df.groupby("customer_id")["customer_name"].first().to_dict()
    at_risk_df["customer_name"] = at_risk_df["customer_id"].map(global_names)
    at_risk_df["last_purchase"] = at_risk_df["last_purchase"].dt.strftime("%Y-%m-%d")
    
    at_risk_list = at_risk_df.sort_values(by="days_inactive", ascending=False).head(10).round(2).to_dict(orient="records")
    
    return {
        "total_customers": total_cust,
        "new_customers": new_cust_count,
        "returning_customers": returning_cust_count,
        "avg_customer_revenue": round(avg_cust_rev, 2),
        "avg_order_frequency": round(avg_freq, 2),
        "repeat_purchase_rate": round(repeat_purchase_rate, 2),
        "top_spent_customers": top_spent_list,
        "top_frequent_customers": top_frequent_list,
        "at_risk_customers": at_risk_list
    }
