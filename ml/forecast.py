"""
Solar generation forecasting engine using a Random Forest ensemble.

This module exposes ``ForecastEngine``, which wraps a pre-trained
``sklearn.ensemble.RandomForestRegressor`` and provides two prediction
entry points:

* ``predict(df)`` — inference on an arbitrary DataFrame of weather/feature rows.
* ``predict_for_date(date_str, weather_df)`` — synthetic 24-hour day forecast
  that aggregates historical same-month weather patterns when live sensor data
  for the target date is unavailable.

Uncertainty quantification is derived from the *ensemble spread* of the
individual trees: the standard deviation across 200 tree predictions is used
to construct a 90 % prediction interval (±1.645 σ).
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime


class ForecastEngine:
    """
    Solar generation forecast engine backed by a Random Forest ensemble.

    The Random Forest approach provides two key advantages for this use case:

    1. **Non-linear weather-to-generation mapping**: irradiance, cloud cover, and
       temperature interact in complex ways that a linear model cannot capture.
       Individual decision trees naturally partition these feature interactions.

    2. **Free uncertainty estimate**: because the model is an ensemble of
       ``n_estimators`` trees, the *spread* of their predictions provides a
       data-driven proxy for forecast uncertainty without requiring a separate
       conformal prediction step.

    The model is trained offline by ``ml/train_forecast.py`` and persisted to
    ``ml/models/forecast_model.joblib``.  The list of required feature names is
    stored alongside the model in ``ml/models/features.json`` so that the
    inference code always uses exactly the same feature set as training.

    Attributes
    ----------
    model : RandomForestRegressor
        Loaded pre-trained scikit-learn model.
    features : list[str]
        Ordered list of feature column names expected by the model.
    """

    def __init__(self, model_path: str, features_path: str):
        self.model = joblib.load(model_path)
        with open(features_path, "r") as f:
            self.features = json.load(f)

    def predict(self, df: pd.DataFrame) -> list:
        """
        Run inference on a DataFrame of weather/feature rows.

        Uncertainty is quantified by collecting predictions from every individual
        decision tree in the ensemble and computing their standard deviation.
        This *tree-level standard deviation* captures epistemic uncertainty
        (model disagreement) but not aleatoric uncertainty (irreducible noise).

        A 90 % prediction interval is formed as ``mean ± 1.645 * std`` (see the
        inline note on the z-score below).  The confidence score is a heuristic
        derived from the coefficient of variation: ``1 - std / (mean + ε)``.

        Parameters
        ----------
        df : pd.DataFrame
            Input data. Must include columns for all features listed in
            ``self.features`` after ``_add_features()`` is applied.  If any
            required column is missing after feature engineering, an empty list
            is returned.

        Returns
        -------
        list[dict]
            One dict per input row with keys: ``timestamp``, ``predicted_generation_kw``,
            ``lower_bound_kw``, ``upper_bound_kw``, ``confidence_score``.
        """
        df = df.copy()
        self._add_features(df)

        # Only keep rows that have all required features
        missing = [f for f in self.features if f not in df.columns]
        if missing:
            return []

        X = df[self.features].fillna(0)

        # Collect predictions from every tree in the ensemble (shape: n_trees × n_rows).
        # The mean gives the point estimate; the std gives the uncertainty proxy.
        tree_preds = np.array([tree.predict(X) for tree in self.model.estimators_])
        mean_pred = tree_preds.mean(axis=0)
        std_pred = tree_preds.std(axis=0)

        results = []
        for i in range(len(X)):
            mean = max(0.0, float(mean_pred[i]))
            std = float(std_pred[i])
            # 1.645 is the z-score for a one-sided 95th percentile (i.e., the
            # two-sided 90 % prediction interval: P(-1.645σ ≤ ε ≤ 1.645σ) ≈ 0.90).
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
        """
        Generate a 24-hour solar forecast for a specific date using historical patterns.

        Because live sensor readings for *future* dates are unavailable, this method
        constructs *synthetic* feature rows by aggregating historical data from the
        same calendar month.  For each of the 24 hours it computes the mean of all
        rows from ``weather_df`` that share the same month *and* hour.  This
        climatological averaging captures the seasonal solar curve (sunrise/sunset
        timing, typical irradiance) without requiring a real-time weather API.

        If no historical data exists for a particular hour (e.g., sparse dataset),
        hard-coded sensible defaults are used: 28 °C, 60 % humidity, 30 % cloud
        cover, 800 W/m² irradiance during daylight (06:00–18:00), else 0.

        Parameters
        ----------
        date_str : str
            Target date in ``YYYY-MM-DD`` format.
        weather_df : pd.DataFrame
            Historical weather/generation dataset (``dataset.csv`` after parsing).
            Must contain a ``timestamp`` column (datetime dtype) and all columns
            needed to derive the model's feature set.

        Returns
        -------
        list[dict]
            24 dicts (one per hour) with keys: ``timestamp``, ``hour``,
            ``predicted_generation_kw``, ``lower_bound_kw``, ``upper_bound_kw``,
            ``confidence_score``, ``actual_generation_kw`` (always ``None``).
        """
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
                # Fall back to hard-coded defaults when historical data is absent
                # for this hour/month combination (avoids NaN propagation).
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
            # 1.645 is the z-score for a one-sided 95th percentile (i.e., the
            # two-sided 90 % prediction interval: P(-1.645σ ≤ ε ≤ 1.645σ) ≈ 0.90).
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
