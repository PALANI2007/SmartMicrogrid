# Edge Case Simulation Results

## Overview

This document describes the four edge-case scenarios supported by the `EdgeCaseSimulator` framework. Each scenario modifies the inputs (solar forecast, battery configuration, or load list) and then runs both the **Baseline Scheduler** and the **Smart (Renewable-Aware) Scheduler** under identical conditions, comparing their outputs.

The framework is implemented in `scheduler/edge_cases.py` and exposed via the API at `GET /api/edge-cases`.

---

## Framework

```
EdgeCaseSimulator.run_scenario(scenario_name, loads, battery_config)
  → { status, violations, schedule, explanation, metrics }
```

**Status values:**
- `PASS` — all assertions satisfied; no critical violations
- `FAIL` — one or more assertions violated

---

## Scenarios

### Scenario 1: Prolonged Monsoon / Cloud Cover

| Property | Value |
|----------|-------|
| **Scenario name** | `monsoon_cloud_cover` |
| **Description** | Simulates extended cloud cover or monsoon season where solar generation is severely reduced |
| **Input modification** | Solar forecast reduced to 0.0–0.5 kW for all 24 hours |
| **Expected behaviour** | Essential loads remain protected and continuously scheduled; flexible loads are shifted to use grid power or battery storage rather than solar |
| **Pass criteria** | `violations.essential == 0` (no essential load interrupted); no runtime crash |

**Test assertions:**
```python
assert result['status'] == 'PASS'
assert result['violations']['essential'] == 0
```

---

### Scenario 2: Low / Rapidly Depleting Battery

| Property | Value |
|----------|-------|
| **Scenario name** | `low_battery` |
| **Description** | Simulates a battery that begins near its minimum State-of-Charge |
| **Input modification** | `initial_soc = 0.22` (barely above `minimum_soc = 0.20`) |
| **Expected behaviour** | The scheduler avoids further discharge; grid import is used as fallback; SOC never drops below `min_soc` |
| **Pass criteria** | `violations.battery == False` (SOC constraint never breached) |

**Test assertions:**
```python
assert result['status'] == 'PASS'
assert result['violations']['battery'] == False
```

---

### Scenario 3: Sudden Essential Load Surge

| Property | Value |
|----------|-------|
| **Scenario name** | `essential_load_surge` |
| **Description** | Simulates an unexpected surge in essential loads (e.g., emergency medical equipment added mid-day) |
| **Input modification** | The simulator internally adds an extra essential load of ~5 kW (`Emergency Medical Equipment`) to the provided load list |
| **Expected behaviour** | All essential loads (including the surge load) are scheduled; flexible loads are shifted or deferred as necessary |
| **Pass criteria** | `violations.essential == 0`; a load named "Emergency" or "Medical" appears in the schedule with `status == "SCHEDULED"` |

**Test assertions:**
```python
assert result['violations']['essential'] == 0
scheduled_names = [s['load_name'] for s in result['schedule'] if s['status'] == 'SCHEDULED']
assert any('Emergency' in n or 'Medical' in n for n in scheduled_names)
```

---

### Scenario 4: Flexible Load Deadline Conflict

| Property | Value |
|----------|-------|
| **Scenario name** | `deadline_conflict` |
| **Description** | Simulates an infeasible scheduling request where the required duration exceeds the available time window |
| **Input modification** | The simulator internally adds a flexible load requiring **5 hours** within a **3-hour window** (e.g., `earliest_start = 10:00`, `latest_finish = 13:00`, `duration = 5h`) |
| **Expected behaviour** | The scheduler correctly identifies the infeasibility and returns `status = "CONFLICT"` with a human-readable explanation; no crash; system continues to schedule other feasible loads |
| **Pass criteria** | At least one schedule entry has `status == "CONFLICT"`; its `explanation` field is non-empty |

**Test assertions:**
```python
conflict_loads = [s for s in result['schedule'] if s['status'] == 'CONFLICT']
assert len(conflict_loads) > 0
assert conflict_loads[0]['explanation'] != ''
```

---

## Summary Table

| Scenario | Modification | Key Assertion | Expected Status |
|----------|-------------|---------------|----------------|
| Monsoon / Cloud Cover | Solar → 0.0–0.5 kW | `essential_violations == 0` | PASS |
| Low Battery | `initial_soc = 0.22` | `battery_violation == False` | PASS |
| Essential Surge | +5 kW essential load | Emergency load SCHEDULED | PASS |
| Deadline Conflict | 5h duration in 3h window | Load status == CONFLICT | PASS |

---

## API Reference

```
GET /api/edge-cases
```

Returns results for all four scenarios run against a default load configuration and battery. Each scenario result includes:
- `scenario_name`
- `status` (`PASS` / `FAIL`)
- `violations` object
- `schedule` list
- `explanation` string
- `metrics` (renewable self-consumption %, grid energy, battery charge/discharge)
