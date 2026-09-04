import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scheduler.metrics import MetricsCalculator

def test_self_consumption_calculation(sample_battery_config):
    calc = MetricsCalculator()
    hourly_gen = [1.0] * 24
    schedules = [{"status": "SCHEDULED", "scheduled_start": "12:00", "scheduled_end": "14:00", "power_kw": 2.0}]
    res = calc.calculate_all(schedules, hourly_gen, sample_battery_config)
    assert res["total_renewable_kwh"] == 24.0

def test_zero_renewable(sample_battery_config):
    calc = MetricsCalculator()
    hourly_gen = [0.0] * 24
    schedules = [{"status": "SCHEDULED", "scheduled_start": "12:00", "scheduled_end": "14:00", "power_kw": 2.0}]
    res = calc.calculate_all(schedules, hourly_gen, sample_battery_config)
    assert res["total_renewable_kwh"] == 0.0

def test_surplus_renewable(sample_battery_config):
    calc = MetricsCalculator()
    hourly_gen = [5.0] * 24
    schedules = [{"status": "SCHEDULED", "scheduled_start": "12:00", "scheduled_end": "14:00", "power_kw": 1.0}]
    res = calc.calculate_all(schedules, hourly_gen, sample_battery_config)
    assert res["total_renewable_kwh"] == 120.0
    assert res["renewable_export_kwh"] > 0
