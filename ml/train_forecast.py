"""
SmartMicrogrid Solar Generation Forecast Training Pipeline.

This script trains a Random Forest regression model to predict hourly solar
generation (kW) from weather and temporal features.  The trained artefacts are
saved to ``ml/models/`` and consumed at runtime by ``ForecastEngine``.

Training pipeline overview
--------------------------
1. **Data loading**: reads ``data/processed/dataset.csv``, parses timestamps,
   and sorts records chronologically.
2. **Feature engineering**: adds temporal features (hour, day-of-week, month,
   is_daytime flag) and auto-regressive solar lag features (1 h, 2 h, 24 h)
   plus rolling-mean features (3 h, 6 h).  Rows with NaN lags (first 24 rows)
   are dropped so that all training samples are complete.
3. **Chronological train/test split**: the first 80 % of rows form the training
   set and the remaining 20 % form the test set.  A *random* split is deliberately
   avoided here because shuffling would allow future solar values to leak into
   the training set via lag features, artificially inflating test metrics.
4. **Model training**: a ``RandomForestRegressor`` with 200 trees is fitted on
   the training split.
5. **Evaluation & baseline comparison**: test-set MAE, RMSE, and R² are computed
   for both the RF model and a naive *same-hour-yesterday* baseline
   (``solar_lag_24h``).  Comparing against the naive baseline confirms the ML
   model adds value beyond simple persistence.
6. **Artefact persistence**: the trained model is saved with ``joblib``, the
   feature list as JSON, and the evaluation metrics as JSON.  These three files
   are all the runtime needs to serve forecasts without re-training.
"""

import os
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train():
    """
    Execute the end-to-end training pipeline and persist model artefacts.

    The function is idempotent: re-running it overwrites the existing artefacts
    with a freshly trained model.  It exits early (with a printed error message)
    if the input dataset is not found.

    Feature engineering
    -------------------
    Temporal features capture seasonal and diurnal patterns:
    - ``hour``         — hour of day (0–23), the strongest driver of solar output.
    - ``day_of_week``  — captures weekend/weekday consumption differences.
    - ``month``        — encodes seasonal variation in sun angle and day length.
    - ``is_daytime``   — binary flag (1 for hours 6–20) to give the model an
                         explicit signal about whether solar generation is
                         physically possible.

    Auto-regressive lag features exploit temporal autocorrelation:
    - ``solar_lag_1h``    — output one hour ago (strong predictor for cloudy periods).
    - ``solar_lag_2h``    — output two hours ago.
    - ``solar_lag_24h``   — same-hour output yesterday (the naive baseline forecast).
    - ``solar_rolling_3h`` — 3-hour rolling mean of lagged output (smooths noise).
    - ``solar_rolling_6h`` — 6-hour rolling mean (captures half-day cloud trends).

    Chronological split
    -------------------
    The dataset is split at the 80th-percentile index (by time) to avoid
    look-ahead bias.  Using ``train_test_split(shuffle=True)`` would allow rows
    with future lag values in the test set to appear as training samples, which
    would leak information and produce over-optimistic test metrics.

    Files saved
    -----------
    ``ml/models/forecast_model.joblib``
        The serialised ``RandomForestRegressor`` (200 trees, random_state=42).
    ``ml/models/features.json``
        Ordered list of feature names; consumed by ``ForecastEngine.__init__``.
    ``ml/models/metrics.json``
        Evaluation metrics for both the RF model and the naive baseline, plus
        ``training_samples`` and ``test_samples`` counts.
    """
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

    # Chronological train/test split — use the first 80 % of time-ordered rows for
    # training and the last 20 % for testing.  Shuffling is intentionally avoided
    # to prevent future lag values from leaking into the training set.
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
