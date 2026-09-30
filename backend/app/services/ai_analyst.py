import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from groq import Groq

from app.core.config import settings
from app.services import sales_analytics, customer_analytics, rfm_analysis, forecasting_service, anomaly_detection

def classify_intent(query: str) -> str:
    """
    Categorize user natural language query into specific analytical intents.
    Uses regex/keyword lookup to guarantee robust, deterministic routing.
    """
    q = query.lower().strip()
    
    # KPIs and overall revenue/profit
    if any(k in q for k in ["revenue", "profit", "margin", "how much money", "kpi", "sales summary", "total sales"]):
        return "get_kpis"
        
    # Product questions
    if any(k in q for k in ["product", "item", "best seller", "best-selling", "highest margin product"]):
        return "get_top_products"
        
    # Regional performance
    if any(k in q for k in ["region", "state", "city", "location", "territory", "geography"]):
        return "get_top_regions"
        
    # Customer risks / churn
    if any(k in q for k in ["at risk", "churn", "inactive", "declining", "lose", "risk"]):
        return "get_customer_risk"
        
    # Future forecasts
    if any(k in q for k in ["forecast", "predict", "future", "projection", "next 30 days", "next month"]):
        return "get_forecast"
        
    # Anomalies and errors
    if any(k in q for k in ["anomaly", "anomalies", "outlier", "irregular", "unusual", "weird", "drop"]):
        return "get_anomalies"
        
    return "general_qa"

def get_ai_explanation(query: str, stats_context: Dict[str, Any]) -> str:
    """
    Submit the factual statistical summary context and user question to Groq.
    Enforces structural boundaries so the LLM acts only as an explanation layer.
    """
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        # Safe fallback if API key is not configured
        context_str = json.dumps(stats_context, indent=2)
        return (
            "### Analytics Engine Calculation (Factual Output)\n\n"
            "Calculated statistics for query:\n"
            f"```json\n{context_str}\n```\n\n"
            "> [!NOTE]\n"
            "> **Groq API Connection Offline**: The backend calculations are complete, but a natural-language "
            "explanation requires a valid `GROQ_API_KEY` in the backend `.env` file."
        )
        
    try:
        # Initialize Groq client
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        system_prompt = (
            "You are a professional Business Intelligence Analyst and Senior Executive Advisor.\n"
            "Your job is to answer user queries using ONLY the trusted pre-calculated metrics provided below.\n\n"
            "CRITICAL RULES:\n"
            "1. You must NEVER calculate, sum, or extrapolate numbers yourself. Only present the pre-calculated values.\n"
            "2. If the statistics do not contain the answer, politely state that you do not have that specific metric in the dataset.\n"
            "3. Separate observed facts from recommendations using distinct markdown headers.\n"
            "4. Format the final output in clean markdown with bullet points and bold highlights.\n"
            "5. Keep the response professional, concise, and business-focused.\n"
        )
        
        user_prompt = (
            f"User Question: \"{query}\"\n\n"
            f"Pre-Calculated Factual Metrics:\n"
            f"```json\n{json.dumps(stats_context, indent=2)}\n```\n"
        )
        
        # Use LLaMA 3.3 70B model for premium analytical writing
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-specdec", # Groq-optimized fast model, fallback to llama-3.1-8b-instant if needed
            temperature=0.2,
            max_tokens=1000
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        # Check fallback to 8b-instant if the specdec model is unavailable
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2,
                max_tokens=1000
            )
            return chat_completion.choices[0].message.content
        except Exception as err:
            return f"Error contacting AI service: {str(err)}. Factual context: {json.dumps(stats_context)}"

def analyze_user_query(file_path: str, query: str) -> str:
    """
    Routes user query to appropriate Pandas analytic calculations,
    and returns an AI-generated explanation of the output.
    """
    # Load dataset
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
        
    df["order_date"] = pd.to_datetime(df["order_date"])
    
    intent = classify_intent(query)
    
    # Fetch relevant metrics based on intent
    stats_context = {"intent_classified": intent}
    
    if intent == "get_kpis":
        overview = sales_analytics.get_sales_overview(df)
        stats_context.update({
            "kpis": overview["kpis"],
            "top_categories": overview["category_distribution"][:3]
        })
    elif intent == "get_top_products":
        # Group by product
        prod_perf = df.groupby("product_name").agg({
            "sales": "sum",
            "quantity": "sum",
            "profit": "sum"
        }).sort_values(by="sales", ascending=False).head(5).round(2).reset_index()
        stats_context.update({
            "top_products_by_revenue": prod_perf.to_dict(orient="records")
        })
    elif intent == "get_top_regions":
        overview = sales_analytics.get_sales_overview(df)
        stats_context.update({
            "regional_sales": overview["regional_distribution"]
        })
    elif intent == "get_customer_risk":
        cust_summary = customer_analytics.get_customer_summary(df)
        stats_context.update({
            "at_risk_customers_count": len(cust_summary["at_risk_customers"]),
            "sample_at_risk_customers": cust_summary["at_risk_customers"][:5]
        })
    elif intent == "get_forecast":
        forecast = forecasting_service.generate_sales_forecast(df, horizon_days=30)
        stats_context.update({
            "forecast_horizon": "30 days",
            "forecast_evaluation_metrics": forecast["metrics"],
            "forecast_sample_future_points": forecast["forecast"][:5] # show first few predictions
        })
    elif intent == "get_anomalies":
        anoms = anomaly_detection.detect_sales_anomalies(df)
        stats_context.update({
            "total_anomalies_found": anoms["anomaly_count"],
            "anomaly_percentage": anoms["anomaly_percentage"],
            "most_abnormal_transactions": anoms["anomalous_transactions"][:5]
        })
    else: # general_qa / fallback
        # Provide general summary to give LLM rich context
        overview = sales_analytics.get_sales_overview(df)
        cust_summary = customer_analytics.get_customer_summary(df)
        stats_context.update({
            "general_metrics": overview["kpis"],
            "total_customers": cust_summary["total_customers"],
            "top_category": overview["category_distribution"][0] if overview["category_distribution"] else None,
            "top_region": overview["regional_distribution"][0] if overview["regional_distribution"] else None
        })
        
    return get_ai_explanation(query, stats_context)

def generate_automated_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Generate automatic facts for the executive dashboard.
    Does not call LLM (completely free/instant, based on calculated facts).
    """
    insights = []
    
    # 1. Sales Insights
    overview = sales_analytics.get_sales_overview(df)
    kpis = overview["kpis"]
    insights.append({
        "category": "Sales",
        "fact": f"Total revenue generated is ${kpis['total_revenue']:,} across {kpis['total_orders']:,} orders.",
        "type": "info"
    })
    
    # 2. Product Insights
    cat_dist = overview["category_distribution"]
    if cat_dist:
        best_cat = max(cat_dist, key=lambda x: x["sales"])
        insights.append({
            "category": "Product",
            "fact": f"Category '{best_cat['category']}' is the top performer, generating ${best_cat['sales']:,} in revenue.",
            "type": "success"
        })
        
    # 3. Regional Insights
    reg_dist = overview["regional_distribution"]
    if reg_dist:
        best_reg = max(reg_dist, key=lambda x: x["sales"])
        insights.append({
            "category": "Region",
            "fact": f"Region '{best_reg['region']}' is the strongest market, with ${best_reg['sales']:,} in total sales.",
            "type": "success"
        })
        
    # 4. Profitability
    margin = kpis["profit_margin"]
    if margin < 15.0:
        insights.append({
            "category": "Profitability",
            "fact": f"Overall profit margin is currently low at {margin}%. Consider reviewing discount structures.",
            "type": "warning"
        })
    else:
        insights.append({
            "category": "Profitability",
            "fact": f"Overall profit margin is healthy at {margin}%.",
            "type": "success"
        })
        
    return insights
