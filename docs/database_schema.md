# Database Schema

## SmartMicrogrid — SQLite Database Schema Reference

**Database file:** `backend/microgrid.db` (production) / `backend/test_microgrid.db` (tests)  
**ORM:** SQLAlchemy (declarative base)  
**Models file:** [`backend/app/models.py`](file:///d:/Project/SmartMicrogrid/backend/app/models.py)

---

## Entity-Relationship Overview

```
loads ──────────────────────────→ schedules
(id PK)                          (load_id FK → loads.id)

solar_data ──────────────────────→ forecasts
(timestamp indexed)              (source data for ML training)

schedules ──────────────────────→ experiment_results
(run_id indexed)                 (run_id links both scheduler runs)

edge_case_results ─── standalone (no FK — scenario results stored as JSON)

validation_responses ─ standalone (no FK — user questionnaire data)

battery_config ──────── standalone (single-row config table)
```

---

## Table 1: `solar_data`

**Purpose:** Stores the historical solar generation time series with associated weather features. This is the training dataset for the Random Forest forecast model. Contains 4,368 hourly rows spanning January–June 2024.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `timestamp` | `DATETIME` | NOT NULL | Hourly timestamp (indexed) |
| `solar_generation_kw` | `FLOAT` | NOT NULL | Measured solar generation in kW |
| `temperature` | `FLOAT` | NOT NULL | Ambient temperature (°C) |
| `humidity` | `FLOAT` | NOT NULL | Relative humidity (%) |
| `cloud_cover` | `FLOAT` | NOT NULL | Cloud cover fraction (0–100) |
| `wind_speed` | `FLOAT` | NOT NULL | Wind speed (m/s) |
| `hour` | `INTEGER` | NOT NULL | Hour of day (0–23), derived feature |
| `day_of_week` | `INTEGER` | NOT NULL | Day of week (0=Monday, 6=Sunday) |
| `month` | `INTEGER` | NOT NULL | Month of year (1–12) |
| `is_weekend` | `BOOLEAN` | NOT NULL | True if Saturday or Sunday |

**Primary Key:** `id`  
**Indexes:** `id`, `timestamp`  
**Foreign Keys:** None

**Notes:** The `hour`, `day_of_week`, `month`, and `is_weekend` columns are pre-computed derived features stored alongside the raw measurements to accelerate ML feature extraction. Night-time rows (hours 0–5 and 20–23) have `solar_generation_kw = 0.0` by definition.

---

## Table 2: `loads`

**Purpose:** Stores the electrical load definitions for the microgrid. Each row represents one appliance or equipment item with its power requirements and scheduling constraints.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `name` | `STRING` | NOT NULL | Load name (e.g., "Water Pump", "Medical Equipment") — indexed |
| `load_type` | `STRING` | NOT NULL | `"essential"` or `"flexible"` |
| `power_kw` | `FLOAT` | NOT NULL | Power consumption in kW |
| `duration_hours` | `FLOAT` | NOT NULL | Required operating duration in hours |
| `earliest_start` | `STRING` | YES | Earliest allowed start time (`"HH:MM"` format), NULL for essential loads |
| `latest_finish` | `STRING` | YES | Latest required finish time (`"HH:MM"` format), NULL for essential loads |
| `priority` | `STRING` | NOT NULL | Scheduling priority: `"high"`, `"medium"`, or `"low"` |
| `is_active` | `BOOLEAN` | NOT NULL | If `False`, load is excluded from scheduling (default `True`) |
| `min_comfort_temp` | `FLOAT` | YES | Optional minimum comfort temperature constraint |
| `max_comfort_temp` | `FLOAT` | YES | Optional maximum comfort temperature constraint |
| `description` | `STRING` | YES | Human-readable description |
| `created_at` | `DATETIME` | NOT NULL | Row creation timestamp (default: `utcnow`) |

**Primary Key:** `id`  
**Indexes:** `id`, `name`  
**Foreign Keys:** None (referenced by `schedules.load_id`)

**Notes:** Essential loads (`load_type="essential"`) always have `earliest_start=NULL` and `latest_finish=NULL` because they run continuously. The `min_comfort_temp` and `max_comfort_temp` fields are reserved for HVAC-type loads and are currently unused by the scheduler.

---

## Table 3: `battery_config`

**Purpose:** Stores the battery energy storage system (BESS) configuration. Typically contains a single row representing the physical battery installed in the microgrid.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `capacity_kwh` | `FLOAT` | NOT NULL | Total battery capacity in kWh |
| `initial_soc` | `FLOAT` | NOT NULL | Initial State-of-Charge fraction (0.0–1.0) for simulation start |
| `minimum_soc` | `FLOAT` | NOT NULL | Minimum allowed SOC fraction (default: 0.20) |
| `maximum_soc` | `FLOAT` | NOT NULL | Maximum allowed SOC fraction (default: 0.95) |
| `max_charge_kw` | `FLOAT` | NOT NULL | Maximum charge rate in kW (default: 3.0) |
| `max_discharge_kw` | `FLOAT` | NOT NULL | Maximum discharge rate in kW (default: 3.0) |
| `charging_efficiency` | `FLOAT` | NOT NULL | Round-trip charging efficiency (default: 0.95) |
| `discharging_efficiency` | `FLOAT` | NOT NULL | Discharging efficiency (default: 0.95) |
| `current_soc` | `FLOAT` | NOT NULL | Live/simulated current State-of-Charge |
| `updated_at` | `DATETIME` | NOT NULL | Last update timestamp |

**Primary Key:** `id`  
**Indexes:** `id`  
**Foreign Keys:** None

**Notes:** `initial_soc` is used as the starting point for 24-hour simulations. `current_soc` is updated after scheduling runs. The `PUT /api/battery` endpoint updates this row in-place (upsert pattern — creates if not exists).

---

## Table 4: `forecasts`

**Purpose:** Stores generated solar forecasts per hour. Each row represents one hour's prediction, including the confidence interval and the actual generation (once known, for error tracking).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `timestamp` | `DATETIME` | NOT NULL | Forecast timestamp (hour resolution) — indexed |
| `predicted_generation_kw` | `FLOAT` | NOT NULL | RF model predicted solar generation (kW) |
| `lower_bound_kw` | `FLOAT` | NOT NULL | Lower confidence bound (kW) |
| `upper_bound_kw` | `FLOAT` | NOT NULL | Upper confidence bound (kW) |
| `confidence_score` | `FLOAT` | NOT NULL | Model confidence score (0.0–1.0) |
| `actual_generation_kw` | `FLOAT` | YES | Actual measured generation (kW) — filled post-hoc |
| `mae` | `FLOAT` | YES | Absolute error for this forecast entry |
| `created_at` | `DATETIME` | NOT NULL | Forecast generation timestamp |

**Primary Key:** `id`  
**Indexes:** `id`, `timestamp`  
**Foreign Keys:** None (source is `solar_data` table, linked logically by timestamp)

**Notes:** When the `ForecastService` generates a forecast for a date, it writes 24 rows to this table. `actual_generation_kw` and `mae` are NULL until the actual measurement is available. Night-time hours have `predicted_generation_kw = 0.0` enforced by the model.

---

## Table 5: `schedules`

**Purpose:** Stores the output of both the baseline and smart scheduler runs. Each row represents one load's scheduled slot for a given scheduling run.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `run_id` | `STRING` | NOT NULL | Unique identifier for the scheduler run — indexed |
| `schedule_type` | `STRING` | NOT NULL | `"baseline"` or `"optimized"` |
| `load_id` | `INTEGER` | NOT NULL | Foreign key → `loads.id` |
| `load_name` | `STRING` | NOT NULL | Denormalized load name (for display without JOIN) |
| `scheduled_start` | `STRING` | NOT NULL | Scheduled start time (`"HH:MM"`) |
| `scheduled_end` | `STRING` | NOT NULL | Scheduled end time (`"HH:MM"`) |
| `scheduled_date` | `DATETIME` | NOT NULL | Date of the schedule |
| `power_kw` | `FLOAT` | NOT NULL | Load power during this slot (kW) |
| `duration_hours` | `FLOAT` | NOT NULL | Scheduled duration (hours) |
| `renewable_available_kw` | `FLOAT` | NOT NULL | Solar generation available at the scheduled slot (kW) |
| `battery_impact_kwh` | `FLOAT` | NOT NULL | Net battery energy impact of scheduling at this slot (kWh) |
| `status` | `STRING` | NOT NULL | `"SCHEDULED"`, `"CONFLICT"`, or `"SKIPPED"` |
| `explanation` | `TEXT` | NOT NULL | Human-readable explanation of the scheduling decision |
| `priority` | `STRING` | NOT NULL | Load priority inherited from `loads.priority` |
| `created_at` | `DATETIME` | NOT NULL | Row creation timestamp |

**Primary Key:** `id`  
**Indexes:** `id`, `run_id`  
**Foreign Keys:** `load_id` → `loads.id`

**Notes:** `load_name` is stored as a denormalized string to allow display of historical schedules even if the original load is later deleted. `explanation` is the XAI text shown to the user explaining why a slot was chosen or why a CONFLICT occurred.

---

## Table 6: `experiment_results`

**Purpose:** Stores the aggregate metrics from baseline vs smart scheduler comparison experiments. Each row represents one full comparison run with performance metrics for the smart scheduler.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `run_id` | `STRING` | NOT NULL | Unique run identifier — indexed |
| `experiment_name` | `STRING` | NOT NULL | Human-readable experiment name |
| `schedule_type` | `STRING` | NOT NULL | Always `"comparison"` for experiment results |
| `renewable_self_consumption_pct` | `FLOAT` | NOT NULL | Smart scheduler renewable self-consumption (%) |
| `renewable_export_kwh` | `FLOAT` | NOT NULL | Exported renewable energy (kWh) |
| `renewable_curtailment_kwh` | `FLOAT` | NOT NULL | Curtailed renewable energy (kWh) |
| `grid_energy_kwh` | `FLOAT` | NOT NULL | Grid energy imported (kWh) |
| `battery_charge_kwh` | `FLOAT` | NOT NULL | Energy charged to battery (kWh) |
| `battery_discharge_kwh` | `FLOAT` | NOT NULL | Energy discharged from battery (kWh) |
| `flexible_completion_rate` | `FLOAT` | NOT NULL | Percentage of flexible loads successfully scheduled |
| `deadline_violations` | `INTEGER` | NOT NULL | Number of deadline violations |
| `comfort_violations` | `INTEGER` | NOT NULL | Number of comfort constraint violations |
| `essential_interruptions` | `INTEGER` | NOT NULL | Number of essential load interruptions (always 0) |
| `user_disruption_score` | `FLOAT` | NOT NULL | Composite user disruption score (lower is better) |
| `total_renewable_kwh` | `FLOAT` | NOT NULL | Total renewable energy generated in the period (kWh) |
| `self_consumed_kwh` | `FLOAT` | NOT NULL | Total self-consumed renewable energy (kWh) |
| `created_at` | `DATETIME` | NOT NULL | Experiment run timestamp |
| `notes` | `TEXT` | YES | Optional notes (e.g., date range, scenario description) |

**Primary Key:** `id`  
**Indexes:** `id`, `run_id`  
**Foreign Keys:** None (linked to `schedules` logically via `run_id + "_baseline"` / `run_id + "_smart"`)

---

## Table 7: `validation_responses`

**Purpose:** Stores stakeholder validation questionnaire responses. Each row represents one survey submission.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `respondent_name` | `STRING` | YES | Respondent's name or identifier (optional) |
| `q1_understandable` | `INTEGER` | NOT NULL | Q1: "How easy was it to understand battery and solar state?" (1–5) |
| `q2_explanation_clear` | `INTEGER` | NOT NULL | Q2: "Did AI explanations help understand why loads were delayed?" (1–5) |
| `q3_disruption` | `INTEGER` | NOT NULL | Q3: "How confident do you feel relying on this for critical loads?" (1–5) |
| `q4_easy_to_read` | `INTEGER` | NOT NULL | Q4: "Was the language switching seamless and accurate?" (1–5) |
| `q5_language_useful` | `INTEGER` | NOT NULL | Q5: "Any confusion when adding flexible loads with time constraints?" (1–5) |
| `q6_confidence_clear` | `INTEGER` | NOT NULL | Q6: "Overall usefulness rating for daily operations" (1–5) |
| `overall_satisfaction` | `FLOAT` | NOT NULL | Computed or direct overall satisfaction score (1.0–5.0) |
| `created_at` | `DATETIME` | NOT NULL | Submission timestamp |
| `notes` | `TEXT` | YES | Optional open-ended comments |

**Primary Key:** `id`  
**Indexes:** `id`  
**Foreign Keys:** None

**Notes:** All six integer columns use a 1–5 Likert scale. `overall_satisfaction` is a float to allow averaged values to be stored. The `GET /api/validation` endpoint computes per-question averages across all rows on every request.

---

## Table 8: `edge_case_results`

**Purpose:** Stores the results of edge case scenario simulations. Each row represents one scenario run.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | `INTEGER` | NOT NULL | Primary key (auto-increment) |
| `scenario_id` | `STRING` | NOT NULL | Scenario identifier — indexed (e.g., `"monsoon_cloud_cover"`) |
| `name` | `STRING` | NOT NULL | Human-readable scenario name |
| `status` | `STRING` | NOT NULL | `"PASS"` or `"FAIL"` |
| `smart_metrics` | `TEXT` | NOT NULL | JSON string of smart scheduler metrics for this scenario |
| `baseline_metrics` | `TEXT` | YES | JSON string of baseline metrics (NULL if not computed) |
| `schedule_summary` | `TEXT` | NOT NULL | JSON string of first 5 schedule entries (summary) |
| `violations` | `TEXT` | NOT NULL | JSON string of violation counts: `{essential, battery, deadline}` |
| `explanation` | `TEXT` | NOT NULL | Human-readable explanation of the scenario outcome |
| `run_at` | `DATETIME` | NOT NULL | Scenario run timestamp |

**Primary Key:** `id`  
**Indexes:** `id`, `scenario_id`  
**Foreign Keys:** None

**Notes:** `smart_metrics`, `baseline_metrics`, `schedule_summary`, and `violations` are stored as JSON strings because their schema varies by scenario. The `GET /api/edge-cases` endpoint parses them back to objects before returning. All four standard scenarios (`monsoon_cloud_cover`, `low_battery`, `essential_load_surge`, `deadline_conflict`) produce `status = "PASS"` in the current implementation.

---

## Schema Initialization

Tables are created automatically on startup via:

```python
@app.on_event("startup")
def on_startup():
    init_db()
```

Where `init_db()` calls `Base.metadata.create_all(bind=engine)`. If the database file already exists with all tables present, this is a no-op (no data is deleted).

**Default seed data** is inserted on first startup:
- 5 sample loads (Medical Equipment, Refrigerator, Water Pump, LED Lights, Irrigation System)
- 1 battery configuration (10 kWh, SOC 50%, min 20%, max 95%)
- 4,368 historical solar data rows (Jan–Jun 2024 synthetic dataset)
