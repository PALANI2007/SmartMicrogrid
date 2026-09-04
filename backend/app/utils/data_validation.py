import pandas as pd
from typing import Tuple, List, Dict
from datetime import datetime

def validate_solar_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    warnings = []
    required_columns = [
        "timestamp", "solar_generation_kw", "temperature", 
        "humidity", "cloud_cover", "wind_speed"
    ]
    
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
            
    df = df.copy()
    
    if (df["solar_generation_kw"] < 0).any():
        warnings.append("Negative solar generation values found. Setting to 0.")
        df.loc[df["solar_generation_kw"] < 0, "solar_generation_kw"] = 0
        
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception as e:
        raise ValueError(f"Invalid timestamp format: {e}")
        
    if df.isnull().any().any():
        warnings.append("Missing values found. Forward and backward filling applied.")
        df = df.ffill().bfill()
        
    return df, warnings

def validate_load(load_data: dict) -> Tuple[bool, str]:
    if load_data.get("power_kw", 0) <= 0:
        return False, "Power must be greater than 0"
        
    if load_data.get("duration_hours", 0) <= 0:
        return False, "Duration must be greater than 0"
        
    if load_data.get("load_type") == "flexible":
        es = load_data.get("earliest_start")
        lf = load_data.get("latest_finish")
        if es and lf:
            try:
                # Basic parsing assumes HH:00 format
                es_h = int(es.split(':')[0])
                lf_h = int(lf.split(':')[0])
                if es_h >= lf_h:
                    return False, "earliest_start must be before latest_finish"
            except Exception:
                return False, "Invalid time format for earliest_start/latest_finish"
                
    valid_priorities = ["high", "medium", "low"]
    if load_data.get("priority") not in valid_priorities:
        return False, f"Priority must be one of {valid_priorities}"
        
    return True, ""

def detect_forecast_error(predicted: float, actual: float, threshold_pct: float = 30.0) -> Dict:
    if actual == 0:
        if predicted == 0:
            error_pct = 0.0
        else:
            error_pct = float('inf') 
    else:
        error_pct = abs(predicted - actual) / actual * 100
        
    is_significant = error_pct > threshold_pct
    direction = "overestimated" if predicted > actual else "underestimated"
    
    return {
        "error_pct": error_pct,
        "is_significant": is_significant,
        "direction": direction
    }
