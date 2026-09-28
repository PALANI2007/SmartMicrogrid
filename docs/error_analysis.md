# Forecast Error Analysis

## Overview

This document reports the distribution of forecast errors for the Random Forest solar generation model on the held-out test set.

---

## Test Period

| Property | Value |
|----------|-------|
| Start date | 2024-05-25 |
| End date | 2024-06-30 |
| Total samples | 869 |

---

## Error Statistics

Error is defined as: `error = predicted - actual`

| Statistic | Value (kW) |
|-----------|-----------|
| Mean Error | 0.0050 |
| Median Error | 0.0000 |
| Std Dev | 0.0644 |
| Min Error | −0.6088 |
| Max Error | 1.2520 |
| MAE | 0.0075 |

---

## Absolute Error Percentiles

| Percentile | Absolute Error (kW) |
|-----------|---------------------|
| P5 | 0.0000 |
| P10 | 0.0000 |
| P25 | 0.0000 |
| P50 | 0.0002 |
| P75 | 0.0017 |
| P90 | 0.0040 |
| P95 | 0.0059 |

---

## Observations

1. **Most errors cluster near zero**: The median absolute error is 0.0002 kW and 75% of errors are below 0.0017 kW. The model is highly accurate for the majority of hours.

2. **Night hours dominate the zero-error band**: Approximately 60% of the 24-hour day has zero or near-zero solar generation. The model correctly predicts zero for these hours, inflating the near-zero percentile counts.

3. **Rare large errors occur at solar generation transitions**: The Min/Max errors (−0.6088 kW, +1.2520 kW) occur at **dawn and dusk** hours when solar generation rises or falls sharply. The lag features do not fully capture the rate of change at these transitions, leading to occasional over- or under-prediction.

4. **Slight positive bias**: The mean error is +0.0050 kW (model slightly over-predicts on average). This is negligible for practical scheduling purposes.

---

## API Access

Forecast error statistics and per-sample errors are accessible via:

```
GET /api/forecast/errors
```

The endpoint returns the statistics table and a histogram-ready array of error values for the current test set.
