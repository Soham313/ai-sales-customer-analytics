import pandas as pd
import pytest
from app.services import sales_analytics, rfm_analysis, forecasting_service, anomaly_detection

@pytest.fixture
def sample_dataframe():
    data = {
        "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-4", "ORD-5"],
        "order_date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"],
        "customer_id": ["C1", "C2", "C1", "C3", "C2"],
        "customer_name": ["Alice", "Bob", "Alice", "Charlie", "Bob"],
        "product_name": ["Laptop", "Mouse", "Laptop", "Keyboard", "Mouse"],
        "category": ["Electronics", "Electronics", "Electronics", "Electronics", "Electronics"],
        "region": ["North", "South", "North", "West", "South"],
        "quantity": [1, 2, 1, 3, 2],
        "unit_price": [1000.0, 25.0, 1000.0, 50.0, 25.0],
        "discount": [0.0, 0.0, 0.1, 0.0, 0.0],
        "sales": [1000.0, 50.0, 900.0, 150.0, 50.0],
        "cost": [600.0, 30.0, 600.0, 90.0, 30.0],
        "profit": [400.0, 20.0, 300.0, 60.0, 20.0]
    }
    return pd.DataFrame(data)

def test_sales_kpi_calculations(sample_dataframe):
    kpis = sales_analytics.compute_kpis(sample_dataframe)
    assert kpis["total_revenue"] == 2150.0
    assert kpis["total_profit"] == 800.0
    assert kpis["total_orders"] == 5
    assert kpis["total_quantity"] == 9
    assert kpis["profit_margin"] == round((800.0 / 2150.0) * 100, 2)

def test_rfm_segments(sample_dataframe):
    rfm_df = rfm_analysis.calculate_rfm_segments(sample_dataframe)
    assert len(rfm_df) == 3 # 3 unique customers (C1, C2, C3)
    assert set(rfm_df.columns).issuperset({"customer_id", "recency", "frequency", "monetary", "r_score", "f_score", "m_score", "segment"})

def test_forecasting_shape(sample_dataframe):
    res = forecasting_service.generate_sales_forecast(sample_dataframe, horizon_days=7)
    assert "historical" in res
    assert "forecast" in res
    assert len(res["forecast"]) == 7
