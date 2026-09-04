import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "dataset.csv")
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"Error: Data file {data_path} not found.")
        return
        
    df = pd.read_csv(data_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    # Feature engineering
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    
    df["solar_lag_1h"] = df["solar_generation_kw"].shift(1)
    df["solar_lag_2h"] = df["solar_generation_kw"].shift(2)
    df["solar_lag_24h"] = df["solar_generation_kw"].shift(24)
    
    df["solar_rolling_3h"] = df["solar_generation_kw"].shift(1).rolling(3).mean()
    df["solar_rolling_6h"] = df["solar_generation_kw"].shift(1).rolling(6).mean()
    
    df["is_daytime"] = df["hour"].apply(lambda x: 1 if 6 <= x <= 20 else 0)
    
    df = df.dropna()
    
    features = [
        "hour", "day_of_week", "month", "temperature_c", "humidity_pct", 
        "cloud_cover_pct", "wind_speed_ms", "irradiance_wm2", 
        "solar_lag_1h", "solar_lag_2h", "solar_lag_24h", 
        "solar_rolling_3h", "solar_rolling_6h", "is_daytime"
    ]
    target = "solar_generation_kw"
    
    X = df[features]
    y = df[target]
    
    # Chronological train/test split
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Baseline comparison (naive forecast: same as yesterday same hour, solar_lag_24h)
    baseline_pred = X_test["solar_lag_24h"]
    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
    baseline_r2 = r2_score(y_test, baseline_pred)
    
    print(f"Random Forest MAE: {mae:.4f}")
    print(f"Random Forest RMSE: {rmse:.4f}")
    print(f"Random Forest R2: {r2:.4f}")
    print(f"Baseline MAE: {baseline_mae:.4f}")
    print(f"Baseline RMSE: {baseline_rmse:.4f}")
    print(f"Baseline R2: {baseline_r2:.4f}")
    
    model_path = os.path.join(models_dir, "forecast_model.joblib")
    features_path = os.path.join(models_dir, "features.json")
    metrics_path = os.path.join(models_dir, "metrics.json")
    
    joblib.dump(model, model_path)
    
    with open(features_path, "w") as f:
        json.dump(features, f)
        
    metrics = {
        "model": {
            "mae": float(mae), 
            "rmse": float(rmse), 
            "r2": float(r2)
        },
        "baseline": {
            "mae": float(baseline_mae), 
            "rmse": float(baseline_rmse), 
            "r2": float(baseline_r2)
        },
        "training_samples": len(X_train),
        "test_samples": len(X_test)
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics, f)
        
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
