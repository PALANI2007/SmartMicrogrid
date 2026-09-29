# API Reference

## SmartMicrogrid — REST API Documentation

**Base URL:** `http://localhost:8000`  
**Framework:** FastAPI (Python)  
**Database:** SQLite via SQLAlchemy  
**Auth:** None (academic prototype — no authentication required)

All error responses follow the format: `{"detail": "..."}` (4xx) or `{"message": "..."}` (5xx).

---

## Endpoint Summary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/forecast` | Get 24-hour solar forecast |
| POST | `/api/forecast/train` | Train/retrain the RF model |
| GET | `/api/forecast/metrics` | Get model vs baseline metrics |
| GET | `/api/forecast/errors` | Get error distribution |
| GET | `/api/forecast/error-analysis` | Get hourly error analysis |
| GET | `/api/forecast/actual-vs-predicted` | Get actual vs predicted data |
| GET | `/api/loads` | List all loads |
| POST | `/api/loads` | Create a new load |
| PUT | `/api/loads/{id}` | Update a load |
| DELETE | `/api/loads/{id}` | Delete a load |
| GET | `/api/battery` | Get battery config and status |
| PUT | `/api/battery` | Update battery config |
| GET | `/api/battery/simulation` | Get 24-hour battery simulation |
| POST | `/api/scheduler/run` | Run the smart scheduler |
| GET | `/api/scheduler/latest` | Get latest optimized schedule |
| GET | `/api/baseline` | Get latest baseline schedule |
| POST | `/api/baseline/run` | Run the baseline scheduler |
| POST | `/api/experiments/run` | Run baseline+smart comparison experiment |
| GET | `/api/experiments/results` | List all experiment results |
| GET | `/api/experiments/results/latest` | Get most recent experiment result |
| GET | `/api/experiments/results/{run_id}` | Get experiment result by run ID |
| GET | `/api/edge-cases` | List saved edge case results |
| POST | `/api/edge-cases/run` | Run one or all edge case scenarios |
| GET | `/api/dashboard` | Get full dashboard metrics |
| GET | `/api/metrics` | Get ML model metrics (alias) |
| POST | `/api/validation` | Submit a validation questionnaire response |
| GET | `/api/validation` | Get all validation responses + averages |

---

## Health

### `GET /api/health`

Returns system health status.

**Response `200 OK`:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Forecast

### `GET /api/forecast`

Returns 24 hourly solar generation forecast points for the specified date (defaults to today).

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date` | `string` | No | Date in `YYYY-MM-DD` format. Defaults to today. |

**Example Request:**
```
GET /api/forecast?date=2024-06-15
```

**Response `200 OK`:** Array of 24 forecast objects.
```json
[
  {
    "timestamp": "2024-06-15T00:00:00",
    "predicted_generation_kw": 0.0,
    "lower_bound_kw": 0.0,
    "upper_bound_kw": 0.0,
    "confidence_score": 0.95,
    "hour": 0
  },
  {
    "timestamp": "2024-06-15T10:00:00",
    "predicted_generation_kw": 4.72,
    "lower_bound_kw": 3.85,
    "upper_bound_kw": 5.59,
    "confidence_score": 0.88,
    "hour": 10
  }
]
```

---

### `POST /api/forecast/train`

Triggers training (or retraining) of the Random Forest solar forecast model using all historical `solar_data` in the database.

**Request Body:** None required.

**Response `200 OK`:**
```json
{
  "status": "success",
  "metrics": {
    "model": {
      "mae": 0.0075,
      "rmse": 0.0646,
      "r2": 0.9979
    },
    "baseline": {
      "mae": 0.4268,
      "rmse": 0.7585,
      "r2": 0.7052
    },
    "training_samples": 3475,
    "test_samples": 869
  }
}
```

---

### `GET /api/forecast/metrics`

Returns the stored model performance metrics from `ml/models/metrics.json`.

**Response `200 OK`:**
```json
{
  "model": {
    "mae": 0.0075,
    "rmse": 0.0646,
    "r2": 0.9979
  },
  "baseline": {
    "mae": 0.4268,
    "rmse": 0.7585,
    "r2": 0.7052
  },
  "training_samples": 3475,
  "test_samples": 869
}
```

---

### `GET /api/forecast/errors`

Returns the full error distribution object, including residuals, percentiles, and MAPE across the test set.

**Response `200 OK`:** Object with error distribution statistics (histogram bins, percentile breakdown, mean absolute percentage error by hour).

---

### `GET /api/forecast/error-analysis`

Returns per-hour mean absolute error (MAE) and best/worst performing hours.

**Response `200 OK`:**
```json
{
  "hourly_mae": {
    "0": 0.0,
    "10": 0.08,
    "14": 0.12
  },
  "best_hour": 0,
  "worst_hour": 14,
  "overall_mae": 0.0075
}
```

---

### `GET /api/forecast/actual-vs-predicted`

Returns historical actual vs predicted generation data for chart display.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `days` | `int` | 30 | Number of past days to include |

**Response `200 OK`:** Array of objects with `timestamp`, `actual_generation_kw`, `predicted_generation_kw`.

---

## Loads

### `GET /api/loads`

Returns all loads in the database.

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "Medical Equipment",
    "load_type": "essential",
    "power_kw": 0.8,
    "duration_hours": 24.0,
    "earliest_start": null,
    "latest_finish": null,
    "priority": "high",
    "is_active": true,
    "min_comfort_temp": null,
    "max_comfort_temp": null,
    "description": "ICU ventilator",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

### `POST /api/loads`

Creates a new load after validating input.

**Request Body:**
```json
{
  "name": "Water Pump",
  "load_type": "flexible",
  "power_kw": 1.5,
  "duration_hours": 2.0,
  "earliest_start": "08:00",
  "latest_finish": "18:00",
  "priority": "medium",
  "is_active": true,
  "description": "Irrigation pump"
}
```

**Validation rules:**
- `power_kw` must be > 0
- `duration_hours` must be > 0
- For `flexible` loads: `earliest_start` must be before `latest_finish`
- `priority` must be `"high"`, `"medium"`, or `"low"`

**Response `200 OK`:** The created load object (same schema as GET).

**Response `400 Bad Request`:**
```json
{"detail": "Power must be greater than 0"}
```

---

### `PUT /api/loads/{load_id}`

Updates an existing load by ID.

**Path Parameters:** `load_id` (integer)

**Request Body:** Same schema as `POST /api/loads`.

**Response `200 OK`:** Updated load object.

**Response `400 Bad Request`:** Validation error detail.

**Response `404 Not Found`:**
```json
{"detail": "Load not found"}
```

---

### `DELETE /api/loads/{load_id}`

Deletes a load by ID.

**Path Parameters:** `load_id` (integer)

**Response `200 OK`:**
```json
{"message": "Deleted"}
```

**Response `404 Not Found`:**
```json
{"detail": "Load not found"}
```

---

## Battery

### `GET /api/battery`

Returns the current battery configuration merged with live status.

**Response `200 OK`:**
```json
{
  "id": 1,
  "capacity_kwh": 10.0,
  "initial_soc": 0.5,
  "minimum_soc": 0.2,
  "maximum_soc": 0.95,
  "max_charge_kw": 3.0,
  "max_discharge_kw": 3.0,
  "charging_efficiency": 0.95,
  "discharging_efficiency": 0.95,
  "current_soc": 0.62,
  "updated_at": "2024-06-15T10:30:00",
  "estimated_energy_kwh": 6.2,
  "usable_energy_kwh": 4.2,
  "status": "normal"
}
```

---

### `PUT /api/battery`

Updates battery configuration parameters.

**Request Body:**
```json
{
  "capacity_kwh": 12.0,
  "minimum_soc": 0.15,
  "maximum_soc": 0.95,
  "max_charge_kw": 4.0,
  "max_discharge_kw": 4.0
}
```

**Response `200 OK`:** Updated battery config object.

---

### `GET /api/battery/simulation`

Runs a 24-hour battery State-of-Charge simulation using the current battery config, all active loads, and today's solar forecast.

**Response `200 OK`:**
```json
{
  "hourly_soc": [0.50, 0.48, 0.47, ..., 0.65],
  "total_charged_kwh": 4.2,
  "total_discharged_kwh": 2.8,
  "min_soc_reached": 0.34,
  "config": {
    "minimum_soc": 0.2,
    "maximum_soc": 0.95,
    "capacity_kwh": 10.0
  }
}
```

---

## Scheduler

### `POST /api/scheduler/run`

Runs the renewable-aware smart scheduler for the specified date, saves results to the database, and returns the schedule with metrics.

**Request Body:**
```json
{
  "date": "2024-06-15"
}
```

**Response `200 OK`:**
```json
{
  "run_id": "run_20240615_143022",
  "date": "2024-06-15",
  "schedule": [
    {
      "load_id": 1,
      "load_name": "Medical Equipment",
      "scheduled_start": "00:00",
      "scheduled_end": "24:00",
      "power_kw": 0.8,
      "duration_hours": 24.0,
      "status": "SCHEDULED",
      "explanation": "Essential load — protected, always scheduled.",
      "renewable_available_kw": 3.2,
      "battery_impact_kwh": 0.0,
      "priority": "high"
    },
    {
      "load_id": 3,
      "load_name": "Water Pump",
      "scheduled_start": "10:00",
      "scheduled_end": "12:00",
      "power_kw": 1.5,
      "duration_hours": 2.0,
      "status": "SCHEDULED",
      "explanation": "Scheduled at 10:00 — peak solar window maximises self-consumption.",
      "renewable_available_kw": 4.8,
      "battery_impact_kwh": -0.3,
      "priority": "medium"
    }
  ],
  "metrics": {
    "total_renewable_kwh": 28.4,
    "self_consumed_kwh": 22.1,
    "renewable_self_consumption_pct": 77.8,
    "renewable_export_kwh": 6.3,
    "renewable_curtailment_kwh": 0.0,
    "grid_energy_kwh": 1.2,
    "battery_charge_kwh": 4.1,
    "battery_discharge_kwh": 2.8,
    "flexible_completion_rate": 100.0,
    "deadline_violations": 0,
    "comfort_violations": 0,
    "user_disruption_score": 0.12
  }
}
```

---

### `GET /api/scheduler/latest`

Returns the most recently saved optimized schedule from the database.

**Response `200 OK`:** Same structure as `POST /api/scheduler/run`, or `null` if no schedule exists.

---

## Baseline

### `GET /api/baseline`

Returns the most recently saved baseline schedule from the database.

**Response `200 OK`:** Same structure as scheduler response but for the naive FCFS baseline, or `null`.

---

### `POST /api/baseline/run`

Runs the naive First-Come-First-Served baseline scheduler for the specified date.

**Request Body:**
```json
{
  "date": "2024-06-15"
}
```

**Response `200 OK`:**
```json
{
  "run_id": "run_20240615_143100_baseline",
  "date": "2024-06-15",
  "schedule": [...],
  "metrics": {
    "renewable_self_consumption_pct": 41.2,
    "renewable_export_kwh": 16.6,
    "grid_energy_kwh": 4.3,
    "deadline_violations": 0,
    "comfort_violations": 0
  }
}
```

---

## Experiments

### `POST /api/experiments/run`

Runs both the baseline and smart schedulers for the specified date, computes improvement metrics, and saves the comparison to the database.

**Request Body:**
```json
{
  "date_str": "2024-06-15",
  "experiment_name": "Summer Peak Day Test"
}
```

**Response `200 OK`:**
```json
{
  "run_id": "run_20240615_143200",
  "experiment_name": "Summer Peak Day Test",
  "date_str": "2024-06-15",
  "baseline": {
    "schedule": [...],
    "metrics": {
      "renewable_self_consumption_pct": 41.2,
      "renewable_export_kwh": 16.6,
      "grid_energy_kwh": 4.3,
      "deadline_violations": 0
    }
  },
  "optimized": {
    "schedule": [...],
    "metrics": {
      "renewable_self_consumption_pct": 77.8,
      "renewable_export_kwh": 6.3,
      "grid_energy_kwh": 1.2,
      "deadline_violations": 0
    }
  },
  "improvements": {
    "renewable_self_consumption_pct": 36.6,
    "renewable_export_kwh": 10.3,
    "grid_energy_kwh": 3.1
  },
  "created_at": "2024-06-15T14:32:00"
}
```

---

### `GET /api/experiments/results`

Returns all experiment results ordered by creation date (newest first).

**Response `200 OK`:** Array of experiment result objects (database column values).

---

### `GET /api/experiments/results/latest`

Returns the most recent experiment result.

**Response `200 OK`:** Single experiment result object.

**Response `404 Not Found`:**
```json
{"detail": "No experiment results found"}
```

---

### `GET /api/experiments/results/{run_id}`

Returns a specific experiment result by its `run_id`.

**Path Parameters:** `run_id` (string)

**Response `200 OK`:** Single experiment result object.

**Response `404 Not Found`:**
```json
{"detail": "Experiment not found"}
```

---

## Edge Cases

### `GET /api/edge-cases`

Returns all saved edge case results ordered by run time (newest first).

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "scenario_id": "monsoon_cloud_cover",
    "name": "Monsoon / Cloud Cover",
    "status": "PASS",
    "smart_metrics": {
      "renewable_self_consumption_pct": 62.1,
      "essential_violations": 0
    },
    "baseline_metrics": null,
    "violations": {
      "essential": 0,
      "battery": false,
      "deadline": 0
    },
    "explanation": "All essential loads protected. Flexible loads shifted to discharge window.",
    "run_at": "2024-06-15T14:00:00"
  }
]
```

---

### `POST /api/edge-cases/run`

Runs one or all edge case scenarios using the current loads and battery configuration from the database.

**Request Body:**
```json
{
  "scenario_id": "all"
}
```

**`scenario_id` options:**

| Value | Scenario Description |
|-------|---------------------|
| `"all"` | Run all 4 scenarios |
| `"monsoon_cloud_cover"` | Near-zero solar for full day (monsoon simulation) |
| `"low_battery"` | Battery starts at near-minimum SOC (22%) |
| `"essential_load_surge"` | Emergency essential load added mid-day |
| `"deadline_conflict"` | Flexible load with infeasible time window |

**Response `200 OK`:**
```json
{
  "scenarios_run": 4,
  "results": [
    {
      "scenario_id": "monsoon_cloud_cover",
      "name": "Monsoon / Cloud Cover",
      "status": "PASS",
      "smart_metrics": {...},
      "baseline_metrics": null,
      "schedule": [...],
      "violations": {"essential": 0, "battery": false, "deadline": 0},
      "explanation": "..."
    },
    {
      "scenario_id": "low_battery",
      "name": "Low Battery SOC",
      "status": "PASS",
      ...
    },
    {
      "scenario_id": "essential_load_surge",
      "name": "Essential Load Surge",
      "status": "PASS",
      ...
    },
    {
      "scenario_id": "deadline_conflict",
      "name": "Deadline Conflict",
      "status": "PASS",
      ...
    }
  ]
}
```

---

## Dashboard

### `GET /api/dashboard`

Returns the full set of metrics for the main dashboard view.

**Response `200 OK`:**
```json
{
  "current_solar_kw": 3.42,
  "predicted_solar_kw": 4.10,
  "total_load_kw": 2.85,
  "essential_load_kw": 1.10,
  "flexible_load_kw": 1.75,
  "battery_soc": 0.68,
  "self_consumption_pct": 74.3,
  "renewable_export_kwh": 5.2,
  "grid_dependency_pct": 8.1,
  "system_status": "good",
  "active_loads": [
    {
      "id": 1,
      "name": "Medical Equipment",
      "load_type": "essential",
      "power_kw": 0.8,
      "status": "SCHEDULED"
    }
  ]
}
```

---

### `GET /api/metrics`

Returns the ML model performance metrics (alias for the same data as `/api/forecast/metrics`).

**Response `200 OK`:** Same as `GET /api/forecast/metrics`.

---

## Validation

### `POST /api/validation`

Submits a stakeholder validation questionnaire response.

**Request Body:**
```json
{
  "respondent_name": "Grid Operator A",
  "q1_understandable": 5,
  "q2_explanation_clear": 4,
  "q3_disruption": 4,
  "q4_easy_to_read": 5,
  "q5_language_useful": 5,
  "q6_confidence_clear": 4,
  "overall_satisfaction": 4.5,
  "notes": "Excellent system, easy to use in Tamil."
}
```

**Score scale:** 1 (strongly disagree / very poor) to 5 (strongly agree / excellent).

**Response `200 OK`:**
```json
{
  "status": "success",
  "id": 1
}
```

---

### `GET /api/validation`

Returns all validation responses with per-question averages.

**Response `200 OK`:**
```json
{
  "responses": [
    {
      "id": 1,
      "respondent_name": "Grid Operator A",
      "q1_understandable": 5,
      "q2_explanation_clear": 4,
      "q3_disruption": 4,
      "q4_easy_to_read": 5,
      "q5_language_useful": 5,
      "q6_confidence_clear": 4,
      "overall_satisfaction": 4.5,
      "created_at": "2024-06-15T15:00:00",
      "notes": "Excellent system, easy to use in Tamil."
    }
  ],
  "averages": {
    "q1_avg": 4.6,
    "q2_avg": 4.2,
    "q3_avg": 4.0,
    "q4_avg": 4.4,
    "q5_avg": 4.8,
    "q6_avg": 4.2,
    "overall_avg": 4.3
  },
  "count": 1
}
```

If no responses exist, `averages` is an empty object `{}` and `count` is `0`.
