import pandas as pd
import numpy as np
import datetime
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

def generate_sales_forecast(df: pd.DataFrame, horizon_days: int = 30) -> Dict[str, Any]:
    """
    Aggregate daily sales and generate a forecasting model using Random Forest.
    Calculates historical daily aggregates, fits time features,
    and returns predictions along with confidence intervals and MAE/RMSE.
    """
    df_copy = df.copy()
    df_copy["order_date"] = pd.to_datetime(df_copy["order_date"])
    
    # 1. Aggregate to daily frequency
    daily_sales = df_copy.groupby("order_date")["sales"].sum().reset_index()
    daily_sales = daily_sales.set_index("order_date")
    
    # Resample to fill gaps (business closed days = 0 sales)
    daily_sales = daily_sales.resample("D").asfreq().fillna(0.0)
    daily_sales = daily_sales.reset_index()
    
    if len(daily_sales) < 3:
        # Insufficient data fallback
        return {
            "historical": daily_sales.rename(columns={"order_date": "date"}).to_dict(orient="records"),
            "forecast": [],
            "metrics": {"mae": 0.0, "rmse": 0.0, "status": "insufficient_data"}
        }
        
    # 2. Feature Engineering
    # We will build calendar and trend features
    def extract_features(data_df):
        df_feats = data_df.copy()
        df_feats["trend"] = np.arange(len(df_feats))
        df_feats["day_of_week"] = df_feats["order_date"].dt.dayofweek
        df_feats["day_of_month"] = df_feats["order_date"].dt.day
        df_feats["month"] = df_feats["order_date"].dt.month
        df_feats["year"] = df_feats["order_date"].dt.year
        return df_feats
        
    featured_data = extract_features(daily_sales)
    
    X = featured_data[["trend", "day_of_week", "day_of_month", "month", "year"]]
    y = featured_data["sales"]
    
    # 3. Chronological Train/Test Split (80% train, 20% test)
    split_idx = int(len(featured_data) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # 4. Model Training & Evaluation
    # Use Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Predict on test
    test_preds = model.predict(X_test)
    
    # Calculate performance metrics
    mae = mean_absolute_error(y_test, test_preds)
    rmse = root_mean_squared_error(y_test, test_preds)
    
    # Calculate Mean Absolute Percentage Error (MAPE)
    non_zero_indices = y_test != 0
    if non_zero_indices.sum() > 0:
        mape = float(np.mean(np.abs((y_test[non_zero_indices] - test_preds[non_zero_indices]) / y_test[non_zero_indices])) * 100)
    else:
        mape = 0.0
        
    # Re-train on all data for future projection
    model.fit(X, y)
    
    # Calculate residuals standard deviation for confidence intervals
    residuals = y - model.predict(X)
    residual_std = float(np.std(residuals))
    
    # 5. Future Projection
    last_date = daily_sales["order_date"].max()
    future_dates = [last_date + datetime.timedelta(days=i) for i in range(1, horizon_days + 1)]
    
    future_df = pd.DataFrame({"order_date": future_dates})
    # Compute future trend and calendar features
    future_featured = extract_features(future_df)
    # Adjust trend variable relative to historical end index
    future_featured["trend"] = np.arange(len(daily_sales), len(daily_sales) + len(future_df))
    
    X_future = future_featured[["trend", "day_of_week", "day_of_month", "month", "year"]]
    
    # Run predictions
    future_preds = model.predict(X_future)
    
    # Construct forecast result dictionary
    forecast_results = []
    for idx, f_date in enumerate(future_dates):
        pred_val = float(future_preds[idx])
        # 95% Confidence Interval: value +/- 1.96 * std
        lower_bound = max(0.0, pred_val - (1.96 * residual_std))
        upper_bound = pred_val + (1.96 * residual_std)
        
        forecast_results.append({
            "date": f_date.strftime("%Y-%m-%d"),
            "sales": round(pred_val, 2),
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "is_forecast": True
        })
        
    # Format historical records
    historical_results = []
    for index, row in daily_sales.iterrows():
        historical_results.append({
            "date": row["order_date"].strftime("%Y-%m-%d"),
            "sales": round(float(row["sales"]), 2),
            "lower_bound": round(float(row["sales"]), 2),
            "upper_bound": round(float(row["sales"]), 2),
            "is_forecast": False
        })
        
    return {
        "historical": historical_results,
        "forecast": forecast_results,
        "metrics": {
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "mape": round(mape, 2),
            "status": "success"
        }
    }
