# ML Solar Forecast Evaluation

## Overview

This document reports the training and evaluation results for the Random Forest solar generation forecasting model used in SmartMicrogrid.

---

## Dataset

| Property | Value |
|----------|-------|
| Total rows | 4,368 |
| Date range | January 2024 – June 2024 |
| Frequency | Hourly (8,784 hourly slots; gaps represent night hours with zero generation) |
| Training samples | 3,475 |
| Test samples | 869 |
| Split strategy | Chronological (no shuffling) — 80% train / 20% test |
| Test period | 2024-05-25 to 2024-06-30 |

The split is **strictly chronological** to avoid data leakage from future to past.

---

## Features

The model uses **14 input features** (stored in `ml/models/features.json`):

| # | Feature | Description |
|---|---------|-------------|
| 1 | `hour` | Hour of day (0–23) |
| 2 | `day_of_week` | Day of week (0=Monday, 6=Sunday) |
| 3 | `month` | Calendar month (1–12) |
| 4 | `temperature_c` | Ambient temperature (°C) |
| 5 | `humidity_pct` | Relative humidity (%) |
| 6 | `cloud_cover_pct` | Cloud cover percentage |
| 7 | `wind_speed_ms` | Wind speed (m/s) |
| 8 | `irradiance_wm2` | Solar irradiance (W/m²) — primary predictor |
| 9 | `solar_lag_1h` | Solar generation lagged by 1 hour |
| 10 | `solar_lag_2h` | Solar generation lagged by 2 hours |
| 11 | `solar_lag_24h` | Solar generation lagged by 24 hours |
| 12 | `solar_rolling_3h` | 3-hour rolling mean of solar generation |
| 13 | `solar_rolling_6h` | 6-hour rolling mean of solar generation |
| 14 | `is_daytime` | Binary flag: 1 if `06:00 ≤ hour ≤ 19:00`, else 0 |

---

## Model Configuration

```
Algorithm:  RandomForestRegressor
n_estimators:  200
random_state:  42
```

---

## Evaluation Results

| Metric | Random Forest | Naive Baseline |
|--------|--------------|----------------|
| MAE (kW) | **0.0075** | 0.4268 |
| RMSE (kW) | **0.0646** | 0.7585 |
| R² | **0.9979** | 0.7052 |

The naive baseline predicts the same-hour value from the previous day (24-hour persistence).

---

## Note on High R²

> **The high R² (0.9979) reflects that the dataset is synthetic and `solar_generation_kw` is derived mathematically from `irradiance_wm2` and `temperature_c` with minimal noise. The model is essentially learning this deterministic relationship. In a real deployment with raw sensor data, performance would be lower.**

---

## Leakage Check

Lag features are computed using `shift(1)` (previous-hour values), **not** `shift(0)` (same-hour values). This ensures no future information leaks into the feature set at training or inference time.

- `solar_lag_1h` = `solar_generation_kw.shift(1)` ✔ (past, not future)
- `solar_lag_2h` = `solar_generation_kw.shift(2)` ✔
- `solar_lag_24h` = `solar_generation_kw.shift(24)` ✔
- Rolling features also use `shift(1)` before rolling to avoid using the current value.

---

## Prediction Uncertainty

The model returns a **point forecast** plus optional lower/upper confidence bounds:

> **Lower/Upper bounds use ±1.645 × std of individual tree predictions (empirical interval, not a statistically guaranteed confidence interval at 90%).**

The bounds reflect the spread of the 200 decision trees in the ensemble and are useful as a rough uncertainty indicator. They are **not** a formal prediction interval derived from a probability model.
