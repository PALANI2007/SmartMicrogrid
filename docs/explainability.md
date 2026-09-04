# AI Evaluator Explainability Guide

A critical component of this 35% milestone is the **Explainability Engine**. Rather than functioning as a black-box optimizer, the scheduler is required to generate human-readable reasoning for every scheduling decision it makes. 

## How It Works
When the `RenewableAwareScheduler` places a load into a time slot, it evaluates:
1. The type of load (Essential vs Flexible).
2. The availability of solar surplus during that hour.
3. The load's priority.
4. Deadline constraints.

It then formats these factors into a localized explanation string.

### Example 1: Essential Loads
**Action**: An essential load (e.g., Medical Equipment) is submitted.
**Scheduler Output**: 
`Status: SCHEDULED`
`Explanation: "Essential load scheduled unconditionally."`
**Reasoning**: Essential loads bypass solar constraints and must be run regardless of grid or battery dependency.

### Example 2: Flexible Loads (Ideal Condition)
**Action**: A Water Pump (2.0 kW) is scheduled for 13:00.
**Scheduler Output**:
`Status: SCHEDULED`
`Explanation: "Water Pump scheduled at 13:00 because solar forecast yields a 5.0 kW surplus, satisfying the 2.0 kW requirement with 0 battery impact."`

### Example 3: Flexible Loads (Conflict)
**Action**: An EV Charger (7.0 kW) is submitted, but the battery is low, solar is 0, and the max grid draw constraint is breached.
**Scheduler Output**:
`Status: CONFLICT`
`Explanation: "Could not schedule EV Charger. Maximum power capacity exceeded. Required 7.0 kW but only 3.0 kW available across all valid time windows before deadline."`

## API Contract
These explanations are returned in the `schedule` array of the `/api/scheduler/latest` endpoint and mapped directly to the frontend's timeline view, ensuring the end-user (and the AI Evaluator) can trace exactly why a specific decision was made.
