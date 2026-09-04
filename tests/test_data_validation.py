import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backend.app.utils.data_validation import validate_solar_data, detect_forecast_error

def test_validate_solar_data_valid():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01 00:00:00"],
        "solar_generation_kw": [1.0],
        "temperature": [20.0],
        "humidity": [50.0],
        "cloud_cover": [0.1],
        "wind_speed": [5.0]
    })
    res, warns = validate_solar_data(df)
    assert len(warns) == 0

def test_validate_solar_data_missing_columns():
    df = pd.DataFrame({"timestamp": ["2024-01-01 00:00:00"]})
    with pytest.raises(ValueError):
        validate_solar_data(df)

def test_validate_solar_data_negative_values():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01 00:00:00"],
        "solar_generation_kw": [-1.0],
        "temperature": [20.0],
        "humidity": [50.0],
        "cloud_cover": [0.1],
        "wind_speed": [5.0]
    })
    res, warns = validate_solar_data(df)
    assert len(warns) == 1
    assert res.iloc[0]["solar_generation_kw"] == 0.0

def test_detect_forecast_error_significant():
    res = detect_forecast_error(10.0, 5.0)
    assert res["is_significant"] == True
    assert res["direction"] == "overestimated"

def test_detect_forecast_error_normal():
    res = detect_forecast_error(10.0, 9.0)
    assert res["is_significant"] == False
