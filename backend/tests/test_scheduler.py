import pytest
from scheduler.baseline_scheduler import BaselineScheduler
from scheduler.constraints import ConstraintChecker
from scheduler.scheduler_engine import RenewableAwareScheduler

def test_baseline_scheduler():
    scheduler = BaselineScheduler()
    # Test that flexible loads are scheduled as early as possible
    loads = [
        {
            "id": 1, "name": "Flexible Load", "load_type": "flexible",
            "power_kw": 2.0, "duration_hours": 2, "earliest_start": "10:00",
            "latest_finish": "14:00", "priority": "low"
        }
    ]
    schedule = scheduler.schedule(loads, "2026-09-04")
    assert len(schedule) == 1
    assert schedule[0]["scheduled_start"] == "10:00"
    assert schedule[0]["status"] == "SCHEDULED"

def test_constraint_checker():
    checker = ConstraintChecker()
    # Mock existing schedules to check power overlap
    existing = [
        {"scheduled_start": "10:00", "scheduled_end": "11:00", "duration_hours": 1, "power_kw": 10.0, "status": "SCHEDULED"}
    ]
    battery = {"current_soc": 50, "minimum_soc": 20, "maximum_soc": 100, "capacity_kwh": 10, "max_charge_kw": 5, "max_discharge_kw": 5}
    
    # max power is usually 15.0. Adding 6.0 should fail.
    load = {"power_kw": 6.0, "duration_hours": 1, "earliest_start": "08:00", "latest_finish": "12:00"}
    res = checker.check_all_constraints(load, 10, 11, 50.0, battery, existing)
    assert res["feasible"] == False
    assert any("power" in v.lower() for v in res["violations"])

def test_essential_load_protection():
    scheduler = RenewableAwareScheduler()
    loads = [
        {
            "id": 1, "name": "Essential Load", "load_type": "essential",
            "power_kw": 1.0, "duration_hours": 24, "earliest_start": "00:00",
            "latest_finish": "23:59", "priority": "high"
        }
    ]
    battery = {"current_soc": 50, "minimum_soc": 20, "maximum_soc": 100, "capacity_kwh": 10, "max_charge_kw": 5, "max_discharge_kw": 5}
    forecast = [{"timestamp": f"2026-09-04T{i:02d}:00:00", "predicted_generation_kw": 5.0} for i in range(24)]
    
    schedule = scheduler.schedule(loads, forecast, battery, "2026-09-04")
    assert len(schedule) == 1
    assert schedule[0]["status"] == "SCHEDULED"
