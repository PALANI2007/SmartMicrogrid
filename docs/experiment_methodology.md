# Experiment Methodology

The 50% milestone introduces a side-by-side Experiment Pipeline (`/api/experiments/run`).

## Pipeline Execution
When an experiment is triggered:
1. The database loads the active user-defined loads and battery configuration.
2. The ML Forecast engine generates a 24-hour prediction for the target date.
3. The **Baseline Scheduler** runs and calculates metrics.
4. The **Renewable-Aware Scheduler** runs and calculates metrics.
5. A comparative payload is saved to the SQLite database and returned.

## Measured Metrics
- `renewable_self_consumption_pct`: Percentage of solar energy consumed locally vs exported. (Higher is better)
- `grid_energy_kwh`: Energy imported from the grid to cover deficits. (Lower is better)
- `renewable_curtailment_kwh`: Surplus solar energy that could not be stored or consumed (exported). (Lower is better)
- `flexible_completion_rate`: Percentage of flexible loads successfully scheduled before deadlines. (Higher is better)
- `user_disruption_score`: Heuristic penalty for missing deadlines or delaying preferred start times. (Lower is better)

By comparing these metrics between the baseline and optimized schedulers, the system empirically proves the value of the ML-driven scheduling approach.
