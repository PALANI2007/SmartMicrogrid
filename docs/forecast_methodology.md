# Forecasting Methodology

## Model Architecture
The forecasting engine uses a **RandomForestRegressor** (200 estimators) to predict hourly solar generation.

## Features
- **Temporal**: `hour`, `day_of_week`, `month`, `is_daytime`
- **Meteorological**: `temperature_c`, `humidity_pct`, `cloud_cover_pct`, `wind_speed_ms`, `irradiance_wm2`
- **Lag/Rolling**: `solar_lag_1h`, `solar_lag_2h`, `solar_lag_24h`, `solar_rolling_3h`, `solar_rolling_6h`

## Uncertainty Bounds
To provide confidence intervals for the constraint-based scheduler:
1. Predictions are generated across all 200 trees in the forest.
2. The `std_pred` (standard deviation across trees) represents uncertainty.
3. Lower/Upper bounds are computed using `±1.645 * std_pred` (approx 90% confidence interval).
4. `confidence_score` is derived from the variance relative to the mean prediction.

## Evaluation
The model is evaluated using a chronological 80/20 train/test split to prevent data leakage.
Performance is compared against a naive baseline (using `solar_lag_24h` as the prediction).

*Metrics achieved in 50% milestone:*
- **Random Forest R²**: ~0.99
- **Baseline R²**: ~0.70
