import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Load, BatteryConfig, SolarData, ExperimentResult
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class MetricsService:
    def get_dashboard_metrics(self, db: Session) -> dict:
        """Return comprehensive dashboard metrics."""
        from ..services.forecast_service import ForecastService
        from ..services.battery_service import BatteryService

        forecast_svc = ForecastService()
        battery_svc = BatteryService()

        today = datetime.now().strftime("%Y-%m-%d")
        forecast = forecast_svc.get_forecast(db, today)

        # Get loads
        loads = db.query(Load).filter(Load.is_active == True).all()
        essential_kw = sum(l.power_kw for l in loads if l.load_type == "essential")
        flexible_kw = sum(l.power_kw for l in loads if l.load_type == "flexible")
        total_load_kw = essential_kw + flexible_kw

        # Get battery
        battery = battery_svc.get_config(db)
        battery_soc = battery.current_soc if battery else 0.5

        # Current hour metrics from forecast
        current_hour = datetime.now().hour
        current_solar = 0.0
        predicted_solar = 0.0
        for f in forecast:
            h = f.get("hour", -1)
            if h == current_hour:
                current_solar = f.get("predicted_generation_kw", 0)
                predicted_solar = f.get("predicted_generation_kw", 0)
                break

        # Calculate daily metrics from forecast
        total_renewable = sum(f.get("predicted_generation_kw", 0) for f in forecast)
        self_consumed = min(total_renewable, total_load_kw * 24)
        renewable_export = max(0, total_renewable - self_consumed)
        grid_energy = max(0, total_load_kw * 24 - self_consumed)
        self_consumption_pct = (self_consumed / total_renewable * 100) if total_renewable > 0 else 0
        grid_dependency_pct = (grid_energy / (total_load_kw * 24) * 100) if total_load_kw > 0 else 0

        # System status
        if battery_soc < 0.25:
            status = "WARNING"
        elif renewable_export > total_renewable * 0.3:
            status = "WARNING"
        else:
            status = "GOOD"

        # Hourly data
        hourly_data = []
        battery_soc_sim = battery_soc
        battery_capacity = battery.capacity_kwh if battery else 10.0
        min_soc = battery.minimum_soc if battery else 0.2
        max_soc = battery.maximum_soc if battery else 0.95
        max_charge = battery.max_charge_kw if battery else 3.0
        max_discharge = battery.max_discharge_kw if battery else 3.0

        for h in range(24):
            solar = forecast[h]["predicted_generation_kw"] if h < len(forecast) else 0
            load = total_load_kw
            surplus = solar - load
            grid = 0.0
            export = 0.0

            if surplus > 0:
                charge = min(surplus, max_charge, (max_soc - battery_soc_sim) * battery_capacity)
                battery_soc_sim = min(max_soc, battery_soc_sim + charge / battery_capacity)
                export = surplus - charge
            else:
                deficit = -surplus
                discharge = min(deficit, max_discharge, (battery_soc_sim - min_soc) * battery_capacity)
                battery_soc_sim = max(min_soc, battery_soc_sim - discharge / battery_capacity)
                grid = max(0, deficit - discharge)

            hourly_data.append({
                "hour": h,
                "solar_kw": round(solar, 2),
                "load_kw": round(load, 2),
                "battery_soc": round(battery_soc_sim, 3),
                "grid_kw": round(grid, 2),
                "export_kw": round(export, 2),
            })

        return {
            "current_solar_kw": round(current_solar, 2),
            "predicted_solar_kw": round(predicted_solar, 2),
            "total_load_kw": round(total_load_kw, 2),
            "essential_load_kw": round(essential_kw, 2),
            "flexible_load_kw": round(flexible_kw, 2),
            "battery_soc": round(battery_soc, 3),
            "renewable_self_consumption_pct": round(self_consumption_pct, 1),
            "renewable_export_kwh": round(renewable_export, 2),
            "grid_dependency_pct": round(grid_dependency_pct, 1),
            "system_status": status,
            "active_loads": [
                {"id": l.id, "name": l.name, "load_type": l.load_type,
                 "power_kw": l.power_kw, "priority": l.priority}
                for l in loads
            ],
            "hourly_data": hourly_data,
        }
