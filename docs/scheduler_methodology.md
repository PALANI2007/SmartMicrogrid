# Scheduler Methodology

The project currently implements two schedulers for A/B testing and baseline comparison.

## 1. Baseline Scheduler
A naive, heuristic scheduler representing standard practice without forecasting intelligence.
- **Strategy**: Schedules flexible loads at the *earliest possible time slot* within their operating window.
- **Awareness**: Zero visibility into battery SOC or solar forecasts.
- **Result**: High grid dependency during non-solar hours and high battery degradation.

## 2. Renewable-Aware Constraint-Based Scheduler
A heuristic engine that optimizes load placement based on renewable surplus and battery constraints.
- **Strategy**: Uses a weighted scoring system across all feasible time slots.
- **Constraints Checked**:
  - `earliest_start` and `latest_finish` deadlines.
  - Required `power_kw` and `duration_hours`.
- **Scoring Metrics**:
  - `renewable_surplus_score`: High score if solar forecast > existing load.
  - `battery_impact_score`: Penalizes slots that draw the battery below the target threshold.
  - `confidence_penalty`: Reduces score if the ML forecast confidence is low.
- **Resolution**: Prioritizes `high` priority loads. Drops `low` priority flexible loads if no feasible slot with positive score is found before the deadline.

*Note: This is currently a heuristic/constraint-based scheduler, not a global optimization solver like MILP.*
