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


def test_edge_case_monsoon():
    """Edge case: prolonged low solar (monsoon/cloud cover)"""
    from scheduler.edge_cases import EdgeCaseSimulator
    sim = EdgeCaseSimulator()
    loads = [
        {'id': 1, 'name': 'Refrigerator', 'load_type': 'essential', 'power_kw': 0.15,
         'duration_hours': 24, 'earliest_start': None, 'latest_finish': None, 'priority': 'high'},
        {'id': 2, 'name': 'Water Pump', 'load_type': 'flexible', 'power_kw': 1.5,
         'duration_hours': 2, 'earliest_start': '07:00', 'latest_finish': '18:00', 'priority': 'medium'},
    ]
    battery = {'capacity_kwh': 10.0, 'initial_soc': 0.7, 'minimum_soc': 0.2,
                'maximum_soc': 0.95, 'max_charge_kw': 3.0, 'max_discharge_kw': 3.0,
                'charging_efficiency': 0.95, 'discharging_efficiency': 0.95}
    result = sim.run_scenario('monsoon_cloud_cover', loads, battery)
    assert result['status'] == 'PASS', f"Monsoon scenario failed: {result['explanation']}"
    assert result['violations']['essential'] == 0


def test_edge_case_low_battery():
    """Edge case: low initial battery SOC"""
    from scheduler.edge_cases import EdgeCaseSimulator
    sim = EdgeCaseSimulator()
    loads = [
        {'id': 1, 'name': 'Medical Equipment', 'load_type': 'essential', 'power_kw': 0.2,
         'duration_hours': 24, 'earliest_start': None, 'latest_finish': None, 'priority': 'high'},
    ]
    battery = {'capacity_kwh': 10.0, 'initial_soc': 0.22, 'minimum_soc': 0.2,
                'maximum_soc': 0.95, 'max_charge_kw': 3.0, 'max_discharge_kw': 3.0,
                'charging_efficiency': 0.95, 'discharging_efficiency': 0.95}
    result = sim.run_scenario('low_battery', loads, battery)
    assert result['status'] == 'PASS', f"Low battery scenario failed: {result['explanation']}"
    assert result['violations']['battery'] == False


def test_edge_case_essential_surge():
    """Edge case: sudden essential load surge"""
    from scheduler.edge_cases import EdgeCaseSimulator
    sim = EdgeCaseSimulator()
    loads = [
        {'id': 1, 'name': 'Refrigerator', 'load_type': 'essential', 'power_kw': 0.15,
         'duration_hours': 24, 'earliest_start': None, 'latest_finish': None, 'priority': 'high'},
    ]
    battery = {'capacity_kwh': 10.0, 'initial_soc': 0.6, 'minimum_soc': 0.2,
                'maximum_soc': 0.95, 'max_charge_kw': 3.0, 'max_discharge_kw': 3.0,
                'charging_efficiency': 0.95, 'discharging_efficiency': 0.95}
    result = sim.run_scenario('essential_load_surge', loads, battery)
    assert result['violations']['essential'] == 0
    # Emergency load should be in schedule
    scheduled_names = [s['load_name'] for s in result['schedule'] if s['status'] == 'SCHEDULED']
    assert any('Emergency' in n or 'Medical' in n for n in scheduled_names)


def test_edge_case_deadline_conflict():
    """Edge case: flexible load deadline conflict (infeasible window)"""
    from scheduler.edge_cases import EdgeCaseSimulator
    sim = EdgeCaseSimulator()
    loads = []  # EdgeCaseSimulator adds the infeasible load internally
    battery = {'capacity_kwh': 10.0, 'initial_soc': 0.6, 'minimum_soc': 0.2,
                'maximum_soc': 0.95, 'max_charge_kw': 3.0, 'max_discharge_kw': 3.0,
                'charging_efficiency': 0.95, 'discharging_efficiency': 0.95}
    result = sim.run_scenario('deadline_conflict', loads, battery)
    conflict_loads = [s for s in result['schedule'] if s['status'] == 'CONFLICT']
    assert len(conflict_loads) > 0, "Expected CONFLICT status for infeasible deadline"
    assert conflict_loads[0]['explanation'] != '', "Expected non-empty explanation"
