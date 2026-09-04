import json
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime


class ForecastEngine:
    def __init__(self, model_path: str, features_path: str):
        self.model = joblib.load(model_path)
        with open(features_path, "r") as f:
            self.features = json.load(f)

    def predict(self, df: pd.DataFrame) -> list:
        """Predict for all rows in df. Returns list of dicts."""
        df = df.copy()
        self._add_features(df)
        
        # Only keep rows that have all required features
        missing = [f for f in self.features if f not in df.columns]
        if missing:
            return []
        
        X = df[self.features].fillna(0)
        
        # Get predictions from individual trees for uncertainty
        tree_preds = np.array([tree.predict(X) for tree in self.model.estimators_])
        mean_pred = tree_preds.mean(axis=0)
        std_pred = tree_preds.std(axis=0)
        
        results = []
        for i in range(len(X)):
            mean = max(0.0, float(mean_pred[i]))
            std = float(std_pred[i])
            lower = max(0.0, mean - 1.645 * std)
            upper = mean + 1.645 * std
            confidence = float(max(0.0, min(1.0, 1.0 - std / (mean + 0.01)))) if mean > 0 else 0.0
            
            ts = None
            if "timestamp" in df.columns:
                ts = df.iloc[i]["timestamp"]
                if hasattr(ts, "isoformat"):
                    ts = ts.isoformat()
                else:
                    ts = str(ts)
            
            results.append({
                "timestamp": ts,
                "predicted_generation_kw": round(mean, 4),
                "lower_bound_kw": round(lower, 4),
                "upper_bound_kw": round(upper, 4),
                "confidence_score": round(confidence, 4),
            })
        return results

    def predict_for_date(self, date_str: str, weather_df: pd.DataFrame) -> list:
        """Generate 24-hour forecast for a specific date using historical weather patterns."""
        try:
            target_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            target_dt = datetime.now()

        # Get data for same month/day patterns
        month = target_dt.month
        month_mask = weather_df["timestamp"].dt.month == month
        month_df = weather_df[month_mask] if month_mask.any() else weather_df

        samples = []
        for hour in range(24):
            hour_mask = month_df["timestamp"].dt.hour == hour
            hour_df = month_df[hour_mask]

            if hour_df.empty:
                row = {
                    "temperature_c": 28.0, "humidity_pct": 60.0,
                    "cloud_cover_pct": 30.0, "wind_speed_ms": 3.0,
                    "irradiance_wm2": 0.0 if (hour < 6 or hour > 18) else 800.0,
                    "solar_generation_kw": 0.0 if (hour < 6 or hour > 18) else 3.0
                }
                hour_series = pd.Series(row)
            else:
                hour_series = hour_df.mean(numeric_only=True)

            ts = target_dt.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            samples.append({
                "timestamp": ts,
                "hour_idx": hour,
                "temperature_c": hour_series.get("temperature_c", 28.0),
                "humidity_pct": hour_series.get("humidity_pct", 60.0),
                "cloud_cover_pct": hour_series.get("cloud_cover_pct", 30.0),
                "wind_speed_ms": hour_series.get("wind_speed_ms", 3.0),
                "irradiance_wm2": hour_series.get("irradiance_wm2", 0.0),
                "solar_generation_kw": hour_series.get("solar_generation_kw", 0.0),
            })

        sample_df = pd.DataFrame(samples)
        self._add_features(sample_df)
        
        for feat in self.features:
            if feat not in sample_df.columns:
                sample_df[feat] = 0.0
                
        X = sample_df[self.features].fillna(0)
        
        tree_preds = np.array([tree.predict(X) for tree in self.model.estimators_])
        mean_pred = tree_preds.mean(axis=0)
        std_pred = tree_preds.std(axis=0)
        
        results = []
        for i in range(24):
            mean = max(0.0, float(mean_pred[i]))
            std = float(std_pred[i])
            lower = max(0.0, mean - 1.645 * std)
            upper = mean + 1.645 * std
            confidence = float(max(0.0, min(1.0, 1.0 - std / (mean + 0.01)))) if mean > 0 else 0.0

            results.append({
                "timestamp": samples[i]["timestamp"].isoformat(),
                "hour": samples[i]["hour_idx"],
                "predicted_generation_kw": round(mean, 4),
                "lower_bound_kw": round(lower, 4),
                "upper_bound_kw": round(upper, 4),
                "confidence_score": round(confidence, 4),
                "actual_generation_kw": None,
            })
            
        return results

    def _add_features(self, df: pd.DataFrame):
        """Add engineered features in-place."""
        if "timestamp" in df.columns:
            df["hour"] = df["timestamp"].dt.hour if hasattr(df["timestamp"].iloc[0], "hour") else df["timestamp"].apply(lambda x: x.hour if hasattr(x, "hour") else 0)
            df["day_of_week"] = df["timestamp"].dt.dayofweek if hasattr(df["timestamp"].iloc[0], "dayofweek") else 0
            df["month"] = df["timestamp"].dt.month if hasattr(df["timestamp"].iloc[0], "month") else 1
        
        df["is_daytime"] = df.get("hour", 12).apply(lambda x: 1 if 6 <= x <= 20 else 0) if "hour" in df.columns else 1
        
        # Lag features - use 0 if not available (single-row prediction)
        if "solar_generation_kw" in df.columns:
            df["solar_lag_1h"] = df["solar_generation_kw"].shift(1).fillna(0)
            df["solar_lag_2h"] = df["solar_generation_kw"].shift(2).fillna(0)
            df["solar_lag_24h"] = df["solar_generation_kw"].shift(24).fillna(0)
            df["solar_rolling_3h"] = df["solar_generation_kw"].shift(1).rolling(3, min_periods=1).mean().fillna(0)
            df["solar_rolling_6h"] = df["solar_generation_kw"].shift(1).rolling(6, min_periods=1).mean().fillna(0)
        else:
            for feat in ["solar_lag_1h", "solar_lag_2h", "solar_lag_24h", "solar_rolling_3h", "solar_rolling_6h"]:
                df[feat] = 0.0
