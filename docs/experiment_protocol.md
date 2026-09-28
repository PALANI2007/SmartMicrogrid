# Experiment Protocol

## Purpose

Compare the **Baseline Scheduler** against the **Smart (Renewable-Aware) Scheduler** under identical, controlled conditions to quantify the benefit of renewable-aware scheduling.

---

## Methodology

Each experiment run executes both schedulers with **exactly the same inputs**:

| Input | Value used by both schedulers |
|-------|-------------------------------|
| Load list | Same loads (essential + flexible) |
| Battery configuration | Same capacity, initial SOC, efficiency parameters |
| Date | Same date |
| Solar forecast | Same hourly forecast data (Smart scheduler uses it; Baseline ignores it but sees the same data for fair metric calculation) |

After scheduling, metrics are computed for each scheduler's output using `MetricsCalculator.calculate_all()`.

**Baseline Scheduler behaviour**: Assigns flexible loads at their `earliest_start` time without considering solar availability.

**Smart Scheduler behaviour**: Assigns flexible loads to the hour-window that maximises the weighted score (renewable coverage, priority, battery impact, time margin).

---

## Metrics Evaluated

The following 9 metrics are recorded for each scheduler in every experiment run:

| # | Metric | Unit | Description |
|---|--------|------|-------------|
| 1 | `renewable_self_consumption_pct` | % | Fraction of generated renewable energy consumed locally |
| 2 | `renewable_export_kwh` | kWh | Renewable energy exported / curtailed |
| 3 | `grid_energy_kwh` | kWh | Total energy imported from the grid |
| 4 | `battery_charge_kwh` | kWh | Total energy stored in the battery |
| 5 | `battery_discharge_kwh` | kWh | Total energy drawn from the battery |
| 6 | `flexible_completion_rate` | % | Percentage of flexible loads successfully scheduled |
| 7 | `deadline_violations` | count | Number of loads that could not be scheduled within their window |
| 8 | `user_disruption_score` | points | Heuristic disruption score (10 pts per deadline violation) |
| 9 | `total_renewable_kwh` | kWh | Total solar energy generated over 24 hours |

---

## Reproducibility

- Each experiment run is assigned a unique `run_id` (UUID or auto-increment).
- All inputs (loads, battery config, date, forecast snapshot) and outputs (schedules, metrics for both schedulers) are stored in **SQLite** (`microgrid2.db`).
- Results can be replayed by reading the stored inputs and re-running either scheduler.

---

## API

### Run an Experiment

```
POST /api/experiments/run
Content-Type: application/json

{
  "date": "2024-06-15",
  "battery_config": { ... },
  "loads": [ ... ]
}
```

**Response:**
```json
{
  "run_id": 42,
  "date": "2024-06-15",
  "baseline": { "schedule": [...], "metrics": {...} },
  "smart": { "schedule": [...], "metrics": {...} },
  "comparison": { "renewable_self_consumption_improvement_pct": 12.5, ... }
}
```

### Retrieve Experiment Results

```
GET /api/experiments/results
GET /api/experiments/results/{run_id}
```

Returns all stored experiment runs or a specific run by ID, including both schedulers' schedules and metrics.

---

## Implementation Details

- Implemented in `scheduler/experiments.py` (`ExperimentRunner` class).
- Stored in the `experiments` table of `microgrid2.db`.
- The `experiments/` directory at project root contains saved experiment result snapshots.
