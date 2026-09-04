import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    return {
        "mae": float(mean_absolute_error(y_test, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "r2": float(r2_score(y_test, y_pred))
    }

def error_analysis(y_pred, y_actual, timestamps):
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps),
        "actual": y_actual,
        "pred": y_pred
    })
    df["error"] = abs(df["actual"] - df["pred"])
    df["hour"] = df["timestamp"].dt.hour
    
    hourly_mae = df.groupby("hour")["error"].mean()
    hourly_counts = df.groupby("hour")["error"].count()
    
    hourly_errors = []
    for h in range(24):
        if h in hourly_mae.index:
            hourly_errors.append({"hour": h, "mae": float(hourly_mae[h]), "count": int(hourly_counts[h])})
            
    best_hour = hourly_mae.idxmin() if not hourly_mae.empty else None
    worst_hour = hourly_mae.idxmax() if not hourly_mae.empty else None
    
    morning = df[(df["hour"] >= 6) & (df["hour"] < 12)]["error"].mean()
    midday = df[(df["hour"] >= 12) & (df["hour"] < 16)]["error"].mean()
    evening = df[(df["hour"] >= 16) & (df["hour"] < 20)]["error"].mean()
    
    # Just basic mocking of high vs low cloud mae without real cloud data here, since we don't have it in df.
    # In real app we'd pass cloud_cover in the dataframe.
    
    return {
        "best_hour": int(best_hour) if best_hour is not None else None,
        "worst_hour": int(worst_hour) if worst_hour is not None else None,
        "morning_mae": float(morning) if not np.isnan(morning) else 0.0,
        "midday_mae": float(midday) if not np.isnan(midday) else 0.0,
        "evening_mae": float(evening) if not np.isnan(evening) else 0.0,
        "high_cloud_mae": 0.0, 
        "low_cloud_mae": 0.0,
        "hourly_errors": hourly_errors
    }
