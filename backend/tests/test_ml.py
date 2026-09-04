import pytest
import pandas as pd
from ml.forecast import ForecastEngine

import os

def test_forecast_engine():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    engine = ForecastEngine(
        model_path=os.path.join(base_dir, "ml/models/forecast_model.joblib"),
        features_path=os.path.join(base_dir, "ml/models/features.json")
    )
    
    # Create mock weather df
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-09-04 00:00:00", periods=24, freq="H"),
        "temperature": [25.0] * 24,
        "humidity": [60.0] * 24,
        "cloud_cover": [20.0] * 24,
        "wind_speed": [5.0] * 24,
        "solar_generation_kw": [0.0] * 24  # for lags
    })
    
    predictions = engine.predict_for_date("2026-09-04", df)
    
    assert len(predictions) == 24
    assert "predicted_generation_kw" in predictions[0]
    assert "lower_bound_kw" in predictions[0]
    assert "upper_bound_kw" in predictions[0]
    assert "confidence_score" in predictions[0]

    # Night time generation should be exactly 0
    night_preds = [p for p in predictions if 0 <= int(p["timestamp"].split("T")[1].split(":")[0]) <= 4 or 20 <= int(p["timestamp"].split("T")[1].split(":")[0]) <= 23]
    for p in night_preds:
        assert p["predicted_generation_kw"] == 0.0
