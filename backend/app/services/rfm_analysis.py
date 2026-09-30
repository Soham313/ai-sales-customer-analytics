import pandas as pd
import numpy as np
from typing import Dict, List, Any

def calculate_rfm_segments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform RFM analysis on the transactions.
    Calculates Recency, Frequency, and Monetary scores (1-5),
    and assigns business segments based on transparent rules.
    """
    df_copy = df.copy()
    df_copy["order_date"] = pd.to_datetime(df_copy["order_date"])
    
    max_date = df_copy["order_date"].max()
    
    # 1. Calculate Recency, Frequency, and Monetary aggregates per customer
    rfm = df_copy.groupby("customer_id").agg({
        "order_date": lambda x: (max_date - x.max()).days, # Recency: Days since last order
        "order_id": "nunique",                            # Frequency: Number of unique orders
        "sales": "sum",                                    # Monetary: Total sales spend
        "customer_name": "first"
    }).rename(columns={
        "order_date": "recency",
        "order_id": "frequency",
        "sales": "monetary"
    })
    
    # 2. Score mapping (1-5 quintiles)
    # Using rank(method='first') inside pd.qcut guarantees equal bin sizes and handles duplicates cleanly
    rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    rfm["rfm_score"] = rfm["r_score"].astype(str) + rfm["f_score"].astype(str) + rfm["m_score"].astype(str)
    
    # 3. Apply transparent business rules for segmentation
    def assign_segment(row) -> str:
        r = row["r_score"]
        f = row["f_score"]
        m = row["m_score"]
        
        # Champions: Bought recently, buy often and spend the most
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
            
        # Loyal Customers: Buy regularly, highly responsive to promotions
        if r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
            
        # Potential Loyalists: Recent spenders, average frequency
        if r >= 4 and f >= 2 and m >= 2:
            return "Potential Loyalists"
            
        # New Customers: Bought recently, low frequency and low spend
        if r >= 4 and f == 1:
            return "New Customers"
            
        # Promising: Recent buyers but haven't spent much
        if r == 3 and f <= 2:
            return "Promising"
            
        # At Risk: Bought often and spent much, but last purchase was long ago
        if r <= 2 and f >= 3 and m >= 3:
            return "At Risk"
            
        # Can't Lose Them: Made big purchases, but haven't bought in a long time
        if r <= 2 and f >= 2 and m >= 4:
            return "Cannot Lose Them"
            
        # About to Sleep: Below average recency, frequency and monetary
        if r == 2 and f <= 2:
            return "About to Sleep"
            
        # Lost / Churned: Lowest recency, frequency and monetary
        return "Lost Customers"
        
    rfm["segment"] = rfm.apply(assign_segment, axis=1)
    
    return rfm.reset_index()

def get_rfm_summary_stats(rfm_df: pd.DataFrame) -> Dict[str, Any]:
    """Compile segment counts, mean metrics per segment, and score distributions."""
    # Count of customers per segment
    segment_counts = rfm_df["segment"].value_counts().to_dict()
    
    # Detailed segment profiles (averages of R, F, M)
    profiles = rfm_df.groupby("segment").agg({
        "customer_id": "count",
        "recency": "mean",
        "frequency": "mean",
        "monetary": "mean"
    }).rename(columns={"customer_id": "customer_count"}).round(2).reset_index()
    
    # Convert profiles to records list
    segment_profiles = profiles.to_dict(orient="records")
    
    # RFM Segment Descriptions for business guidance
    descriptions = {
        "Champions": "Your best customers. They buy frequently, spend heavily, and purchased very recently. Reward them with exclusive previews and loyalty perks.",
        "Loyal Customers": "Regular buyers who spend a respectable amount. Nurture them with personalized loyalty programs and value bundles.",
        "Potential Loyalists": "Recent shoppers with good average spend and frequency. Upsell them with product recommendations and reviews.",
        "New Customers": "First-time buyers who ordered recently. Welcome them with email onboarding and discount codes for their next purchase.",
        "Promising": "Recent shoppers who haven't spent much yet. Target them with product recommendations to encourage repeat buys.",
        "At Risk": "High-value buyers who haven't shopped in a while. Run re-engagement campaigns, win-back discounts, and customer feedback surveys.",
        "Cannot Lose Them": "Historically big spenders who haven't returned in a long time. Offer massive incentives or personal sales outreach.",
        "About to Sleep": "Below average frequency and recency. Share educational content and limited-time discount offers to wake them up.",
        "Lost Customers": "Lowest recency, frequency, and monetary scores. De-prioritize marketing spend or run a final churn survey."
    }
    
    # Add descriptions to profiles
    for prof in segment_profiles:
        prof["description"] = descriptions.get(prof["segment"], "N/A")
        
    return {
        "counts": segment_counts,
        "profiles": segment_profiles,
        "metrics_distribution": {
            "recency_avg": float(rfm_df["recency"].mean()),
            "frequency_avg": float(rfm_df["frequency"].mean()),
            "monetary_avg": float(rfm_df["monetary"].mean())
        }
    }
