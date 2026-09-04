import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scheduler.baseline_scheduler import BaselineScheduler
from scheduler.scheduler_engine import RenewableAwareScheduler

def test_baseline_scheduler_normal(sample_loads):
    scheduler = BaselineScheduler()
    schedules = scheduler.schedule(sample_loads, "2024-01-01")
    assert len(schedules) == len(sample_loads)
    for s in schedules:
        if s["load_name"] == "Water Pump":
            assert s["status"] == "SCHEDULED"

def test_baseline_scheduler_deadline_conflict(sample_loads):
    scheduler = BaselineScheduler()
    # Force a deadline conflict by making the window too small
    sample_loads[2]["latest_finish"] = "09:00"
    schedules = scheduler.schedule(sample_loads, "2024-01-01")
    for s in schedules:
        if s["load_name"] == "Water Pump":
            assert s["status"] == "CONFLICT"

def test_smart_scheduler_normal(sample_loads, sample_forecast, sample_battery_config):
    scheduler = RenewableAwareScheduler()
    schedules = scheduler.schedule(sample_loads, sample_forecast, sample_battery_config, "2024-01-01")
    assert len(schedules) == len(sample_loads)

def test_smart_scheduler_low_battery(sample_loads, sample_forecast, sample_battery_config):
    scheduler = RenewableAwareScheduler()
    sample_battery_config["initial_soc"] = 0.2
    schedules = scheduler.schedule(sample_loads, sample_forecast, sample_battery_config, "2024-01-01")
    assert len(schedules) == len(sample_loads)

def test_smart_scheduler_deadline_conflict(sample_loads, sample_forecast, sample_battery_config):
    scheduler = RenewableAwareScheduler()
    sample_loads[2]["latest_finish"] = "09:00"
    schedules = scheduler.schedule(sample_loads, sample_forecast, sample_battery_config, "2024-01-01")
    for s in schedules:
        if s["load_name"] == "Water Pump":
            assert s["status"] == "CONFLICT"

def test_essential_loads_protected(sample_loads, sample_forecast, sample_battery_config):
    scheduler = RenewableAwareScheduler()
    schedules = scheduler.schedule(sample_loads, sample_forecast, sample_battery_config, "2024-01-01")
    for s in schedules:
        if s["load_name"] == "Medical Equipment":
            assert s["scheduled_start"] == "00:00"
            assert s["scheduled_end"] == "24:00"

def test_smart_scheduler_load_spike(sample_loads, sample_forecast, sample_battery_config):
    scheduler = RenewableAwareScheduler()
    sample_loads.append({"id": 99, "name": "Spike", "load_type": "flexible", "power_kw": 10.0, "duration_hours": 1.0, "earliest_start": "12:00", "latest_finish": "13:00", "priority": "high"})
    schedules = scheduler.schedule(sample_loads, sample_forecast, sample_battery_config, "2024-01-01")
    assert len(schedules) == len(sample_loads)
