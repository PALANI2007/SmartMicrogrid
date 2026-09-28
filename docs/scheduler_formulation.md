# Scheduler Mathematical Formulation

## Overview

The SmartMicrogrid scheduler is a **greedy heuristic** that assigns flexible loads to hour-long time slots by maximising a weighted scoring function. It does **not** solve a Mixed-Integer Linear Programme (MILP) and does **not** guarantee the globally optimal solution.

> **Note:** This is a greedy heuristic, not a global optimizer. It does not guarantee the globally optimal solution.

---

## Decision Variables

| Symbol | Description |
|--------|-------------|
| `G(t)` | Renewable (solar) generation at hour `t` (kW) |
| `L_e` | Total essential load power — runs continuously 00:00–24:00 (kW) |
| `L_f(i)` | Power of flexible load `i` (kW) |
| `B(t)` | Battery State-of-Charge at hour `t` (fraction, 0–1) |
| `x(i, t)` | Binary scheduling decision: 1 if flexible load `i` starts at hour `t`, else 0 |
| `Grid(t)` | Grid import at hour `t` (kW, non-negative) |

---

## Objective Function

For each candidate start slot `t` for flexible load `i`, the scheduler computes a scalar score and selects the slot with the highest value:

```
Score(i, t) = 2.0 × avg_renewable + 1.0 × priority_score + 1.5 × (1 - |battery_impact|) + 0.5 × time_margin
```

Where:

| Term | Weight | Meaning |
|------|--------|---------|
| Average renewable generation over slot (`avg_renewable`) | **2.0** | Prefer slots with high solar availability |
| Priority score (`priority_score`) | **1.0** | `high`→3, `medium`→2, `low`→1 |
| Battery impact factor `(1 - |battery_impact|)` | **1.5** | Penalise slots that drain the battery |
| Time margin / slack (`time_margin`) | **0.5** | Prefer earlier slots to preserve flexibility for lower-priority loads |

**Battery impact calculation (per slot):**

```
surplus(t) = avg_renewable - ExistingPower(t) - L_f(i)
battery_impact = min(0, surplus(t)) × duration   # negative when deficit
```

The full scoring formula as implemented in `scheduler_engine.py` (line 81):

```python
score = (2.0 * avg_renewable) + (1.0 * priority_score) + (1.5 * (1 - abs(battery_impact))) + (0.5 * time_margin)
```

---

## Constraints

All constraints are evaluated by `constraints.py`. A slot is only eligible if **all** constraints pass.

### 1. Essential Load Constraint

Essential loads (`load_type == "essential"`) are always scheduled for the full 24-hour period and are never shifted. They are not subject to the scoring loop.

```
For all essential loads i: scheduled 00:00 – 24:00 unconditionally
```

### 2. Time Window Constraint

A flexible load must start no earlier than `earliest_start` and must finish by `latest_finish`:

```
t_start >= earliest_start
t_start + duration <= latest_finish
```

The candidate slot range is therefore: `t_start ∈ [earliest_start, latest_finish − duration]`

### 3. Duration Constraint

The scheduled duration must equal the required duration:

```
t_end - t_start = required_duration
```

### 4. Battery SOC Constraint

Battery State-of-Charge is tracked and must remain within configured bounds:

```
min_soc <= B(t) <= max_soc    for all t
```

Defaults: `min_soc = 0.20`, `max_soc = 0.95`

### 5. Power Capacity Constraint

The aggregate load in any single hour must not exceed the maximum system power capacity (default 15 kW):

```
sum of all active load powers at hour t <= 15.0 kW
```

### 6. Deadline Enforcement

If no feasible slot exists (all candidate slots fail at least one constraint), the load is marked `CONFLICT`:

```
status = "CONFLICT"   if no feasible t exists
```

---

## Battery Model

The battery SOC evolves hour-by-hour according to:

```
B(t+1) = B(t) + η_charge × charge(t) / capacity − discharge(t) / (η_discharge × capacity)
```

Where:

| Parameter | Symbol | Default |
|-----------|--------|---------|
| Battery capacity | `capacity` | `capacity_kwh` (kWh) |
| Charging efficiency | `η_charge` | `charging_efficiency` = 0.95 |
| Discharging efficiency | `η_discharge` | `discharging_efficiency` = 0.95 |
| Max charge rate | — | `max_charge_kw` = 3.0 kW |
| Max discharge rate | — | `max_discharge_kw` = 3.0 kW |

**Surplus/deficit logic (from `metrics.py`):**

- If `gen > load`: charge battery up to `max_charge_kw`; surplus beyond that is exported/curtailed.
- If `load > gen`: discharge battery up to `max_discharge_kw`; remaining deficit is imported from the grid.

---

## Power Balance Equation

At each hour `t`:

```
G(t) + discharge(t) + Grid(t) = L(t) + charge(t) + Curtail(t)
```

Where `L(t)` is the total scheduled load (essential + active flexible loads) at hour `t`.

---

## Priority Ordering

Flexible loads are sorted in descending priority before scheduling. Higher-priority loads are assigned their best slot first.

| Priority Label | Numeric Value |
|----------------|--------------|
| `high` | 3 |
| `medium` | 2 |
| `low` | 1 |

---

## Infeasibility Handling

When no feasible time slot exists for a flexible load (e.g., the window is too narrow for the required duration, or all slots violate power capacity), the scheduler sets:

```
status = "CONFLICT"
explanation = "No feasible time slot found within window matching constraints."
```

The load is still returned in the schedule list so the user can inspect and resolve the conflict.

---

## Algorithm Pseudocode

```
Sort flexible loads by priority (high → low)
For each flexible load i:
    best_score = -∞
    For each candidate start_h in [earliest_start, latest_finish - duration]:
        If check_all_constraints(load, start_h) is feasible:
            score = 2.0×avg_renewable + 1.0×priority + 1.5×(1−|battery_impact|) + 0.5×time_margin
            If score > best_score: best_score = score; best_slot = start_h
    If best_slot found: schedule at best_slot; else: status = CONFLICT
```

---

## Limitations

- **Greedy, not global**: Loads are scheduled one at a time in priority order. A later load cannot improve the slot choice of an earlier one.
- **No battery SOC look-ahead**: Battery impact is estimated from the surplus/deficit at the candidate slot only; it does not simulate the full 24-hour battery trajectory.
- **No preemption**: Once a load is scheduled, its slot is fixed for the rest of the run.
- **Hourly granularity**: All decisions are made at 1-hour resolution.
