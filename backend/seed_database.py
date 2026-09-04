import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models import Load, BatteryConfig, ValidationResponse, SolarData, Forecast

def seed():
    init_db()
    db = SessionLocal()
    
    if db.query(Load).count() == 0:
        loads = [
            Load(name="Refrigerator", load_type="essential", power_kw=0.3, duration_hours=24.0, priority="high"),
            Load(name="Medical Equipment", load_type="essential", power_kw=0.8, duration_hours=24.0, priority="high"),
            Load(name="Water Pump", load_type="flexible", power_kw=1.5, duration_hours=2.0, earliest_start="08:00", latest_finish="18:00", priority="high"),
            Load(name="Washing Machine", load_type="flexible", power_kw=0.8, duration_hours=1.0, earliest_start="09:00", latest_finish="20:00", priority="medium"),
            Load(name="Water Heater", load_type="flexible", power_kw=2.0, duration_hours=1.0, earliest_start="10:00", latest_finish="17:00", priority="medium"),
            Load(name="EV Charging", load_type="flexible", power_kw=3.3, duration_hours=3.0, earliest_start="18:00", latest_finish="07:00", priority="high")
        ]
        db.add_all(loads)
        
    if db.query(BatteryConfig).count() == 0:
        b = BatteryConfig(
            capacity_kwh=10.0, initial_soc=0.5, minimum_soc=0.2, maximum_soc=0.95,
            max_charge_kw=3.0, max_discharge_kw=3.0, charging_efficiency=0.95, discharging_efficiency=0.95,
            current_soc=0.5
        )
        db.add(b)
        
    if db.query(ValidationResponse).count() < 5:
        responses = []
        for i in range(1, 6):
            v = ValidationResponse(
                respondent_name=f"Demo User {i}",
                q1_understandable=5 - (i%2), 
                q2_explanation_clear=4 + (i%2), 
                q3_disruption=2 + (i%2), 
                q4_easy_to_read=5, 
                q5_language_useful=4, 
                q6_confidence_clear=5, 
                overall_satisfaction=4.0 + (i%2)*0.5
            )
            responses.append(v)
        db.add_all(responses)
        
    # Seed solar data if exists
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "dataset.csv")
    if os.path.exists(data_path) and db.query(SolarData).count() == 0:
        df = pd.read_csv(data_path).head(4380)
        solar_records = []
        for _, row in df.iterrows():
            ts = pd.to_datetime(row["timestamp"])
            s = SolarData(
                timestamp=ts,
                solar_generation_kw=row.get("solar_generation_kw", 0),
                temperature=row.get("temperature", 0),
                humidity=row.get("humidity", 0),
                cloud_cover=row.get("cloud_cover", 0),
                wind_speed=row.get("wind_speed", 0),
                hour=ts.hour,
                day_of_week=ts.dayofweek,
                month=ts.month,
                is_weekend=ts.dayofweek >= 5
            )
            solar_records.append(s)
        db.bulk_save_objects(solar_records)
        
    # Generate 24 Forecast records for today
    today = datetime.now().replace(minute=0, second=0, microsecond=0)
    if db.query(Forecast).filter(Forecast.timestamp >= today.replace(hour=0)).count() < 24:
        forecasts = []
        for h in range(24):
            ts = today.replace(hour=h)
            if 6 <= h <= 18:
                x = (h - 6) / 12.0
                mean = 6.0 * 4 * x * (1 - x)
            else:
                mean = 0.0
            f = Forecast(
                timestamp=ts,
                predicted_generation_kw=round(mean, 3),
                lower_bound_kw=max(0, round(mean * 0.85, 3)),
                upper_bound_kw=round(mean * 1.15, 3),
                confidence_score=0.85,
            )
            forecasts.append(f)
        db.add_all(forecasts)
        
    db.commit()
    db.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed()
