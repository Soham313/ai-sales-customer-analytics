import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

def apply_filters(df: pd.DataFrame, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Helper function to apply standard filters to the Pandas DataFrame."""
    if not filters:
        return df.copy()
        
    filtered_df = df.copy()
    
    # Date Range Filter
    if "start_date" in filters and filters["start_date"]:
        filtered_df = filtered_df[filtered_df["order_date"] >= pd.to_datetime(filters["start_date"])]
    if "end_date" in filters and filters["end_date"]:
        filtered_df = filtered_df[filtered_df["order_date"] <= pd.to_datetime(filters["end_date"])]
        
    # Categorical Filters
    for key in ["region", "category", "product_name"]:
        if key in filters and filters[key]:
            val = filters[key]
            if isinstance(val, list):
                filtered_df = filtered_df[filtered_df[key].isin(val)]
            else:
                filtered_df = filtered_df[filtered_df[key] == val]
                
    return filtered_df

def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate key financial performance metrics from a cleaned sales dataframe."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_cost": 0.0,
            "total_profit": 0.0,
            "profit_margin": 0.0,
            "total_orders": 0,
            "total_quantity": 0,
            "average_order_value": 0.0,
            "average_selling_price": 0.0
        }
        
    total_revenue = float(df["sales"].sum())
    total_cost = float(df["cost"].sum()) if "cost" in df.columns else 0.0
    total_profit = float(df["profit"].sum()) if "profit" in df.columns else 0.0
    
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    
    # Orders count based on unique ID
    order_col = "order_id" if "order_id" in df.columns else df.index.name or "index"
    total_orders = int(df[order_col].nunique()) if order_col in df.columns else len(df)
    
    total_quantity = int(df["quantity"].sum())
    
    avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0.0
    avg_selling_price = (total_revenue / total_quantity) if total_quantity > 0 else 0.0
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "average_order_value": round(avg_order_value, 2),
        "average_selling_price": round(avg_selling_price, 2)
    }

def get_sales_overview(df: pd.DataFrame, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Calculate dashboard metrics including KPIs, trend aggregations, and categorical distributions."""
    # Convert order_date to datetime if not already
    df["order_date"] = pd.to_datetime(df["order_date"])
    
    # Filter dataset
    filtered_df = apply_filters(df, filters)
    
    # 1. Compute Overall KPIs
    kpis = compute_kpis(filtered_df)
    
    if filtered_df.empty:
        return {
            "kpis": kpis,
            "revenue_trend": [],
            "category_distribution": [],
            "regional_distribution": []
        }
        
    # 2. Compute Sales Trend (Group by day/week/month depending on length)
    min_date = filtered_df["order_date"].min()
    max_date = filtered_df["order_date"].max()
    days_span = (max_date - min_date).days
    
    if days_span <= 60:
        freq = "D"
    elif days_span <= 365:
        freq = "W"
    else:
        freq = "ME"
        
    trend = filtered_df.groupby(pd.Grouper(key="order_date", freq=freq)).agg({
        "sales": "sum",
        "profit": "sum",
        "quantity": "sum"
    }).reset_index()
    
    # Format date strings for chart frontend compatibility
    trend["date"] = trend["order_date"].dt.strftime("%Y-%m-%d" if freq == "D" else "%Y-%m-%d")
    trend = trend.drop(columns=["order_date"])
    revenue_trend = trend.to_dict(orient="records")
    
    # 3. Category distribution
    cat_dist = filtered_df.groupby("category").agg({
        "sales": "sum",
        "profit": "sum"
    }).reset_index()
    cat_dist["margin"] = np.where(cat_dist["sales"] > 0, (cat_dist["profit"] / cat_dist["sales"]) * 100, 0.0)
    cat_dist = cat_dist.round(2).to_dict(orient="records")
    
    # 4. Regional distribution
    reg_dist = filtered_df.groupby("region").agg({
        "sales": "sum",
        "profit": "sum"
    }).reset_index()
    reg_dist = reg_dist.round(2).to_dict(orient="records")
    
    return {
        "kpis": kpis,
        "revenue_trend": revenue_trend,
        "category_distribution": cat_dist,
        "regional_distribution": reg_dist
    }

def get_sales_growth(df: pd.DataFrame, start_date: str, end_date: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compare a primary date range against the prior period to calculate growth rates."""
    df["order_date"] = pd.to_datetime(df["order_date"])
    
    curr_start = pd.to_datetime(start_date)
    curr_end = pd.to_datetime(end_date)
    days_delta = (curr_end - curr_start).days
    
    # Calculate previous range
    prev_start = curr_start - datetime.timedelta(days=days_delta + 1)
    prev_end = curr_start - datetime.timedelta(days=1)
    
    # Extract current and previous datasets
    curr_filters = (filters or {}).copy()
    curr_filters["start_date"] = curr_start
    curr_filters["end_date"] = curr_end
    curr_df = apply_filters(df, curr_filters)
    
    prev_filters = (filters or {}).copy()
    prev_filters["start_date"] = prev_start
    prev_filters["end_date"] = prev_end
    prev_df = apply_filters(df, prev_filters)
    
    # Calculate KPIs
    curr_kpis = compute_kpis(curr_df)
    prev_kpis = compute_kpis(prev_df)
    
    # Compute growth percentages
    growth = {}
    for key in ["total_revenue", "total_profit", "total_orders", "total_quantity", "average_order_value"]:
        curr_val = curr_kpis[key]
        prev_val = prev_kpis[key]
        
        if prev_val == 0:
            growth[key] = 100.0 if curr_val > 0 else 0.0
        else:
            growth[key] = round(((curr_val - prev_val) / prev_val) * 100.0, 2)
            
    return {
        "current_period": curr_kpis,
        "previous_period": prev_kpis,
        "growth": growth,
        "ranges": {
            "current": [curr_start.strftime("%Y-%m-%d"), curr_end.strftime("%Y-%m-%d")],
            "previous": [prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")]
        }
    }
import datetime
