import pytest
from datetime import datetime

@pytest.fixture
def sample_loads():
    return [
        {"id": 1, "name": "Medical Equipment", "load_type": "essential", "power_kw": 0.8, "duration_hours": 24.0, "priority": "high"},
        {"id": 2, "name": "Refrigerator", "load_type": "essential", "power_kw": 0.3, "duration_hours": 24.0, "priority": "high"},
        {"id": 3, "name": "Water Pump", "load_type": "flexible", "power_kw": 1.5, "duration_hours": 2.0, "earliest_start": "08:00", "latest_finish": "18:00", "priority": "high"}
    ]

@pytest.fixture
def sample_forecast():
    return [{"timestamp": datetime(2024, 1, 1, h), "predicted_generation_kw": 5.0 if 8 <= h <= 17 else 0.0} for h in range(24)]

@pytest.fixture
def sample_battery_config():
    return {
        "capacity_kwh": 10.0,
        "initial_soc": 0.5,
        "minimum_soc": 0.2,
        "maximum_soc": 0.95,
        "max_charge_kw": 3.0,
        "max_discharge_kw": 3.0,
        "charging_efficiency": 0.95,
        "discharging_efficiency": 0.95
    }
