from typing import List, Dict
from datetime import datetime

class BaselineScheduler:
    def schedule(self, loads: List[Dict], date_str: str) -> List[Dict]:
        schedules = []
        for load in loads:
            if load.get("load_type") == "essential":
                schedules.append({
                    "load_id": load["id"],
                    "load_name": load["name"],
                    "scheduled_start": "00:00",
                    "scheduled_end": "24:00",
                    "scheduled_date": date_str,
                    "power_kw": load["power_kw"],
                    "duration_hours": 24.0,
                    "renewable_available_kw": 0.0,
                    "battery_impact_kwh": 0.0,
                    "status": "SCHEDULED",
                    "explanation": "Essential load runs continuously.",
                    "priority": load.get("priority", "high")
                })
            else:
                # Flexible load
                duration = int(load.get("duration_hours", 1))
                es_str = load.get("earliest_start")
                lf_str = load.get("latest_finish")
                
                es = int(es_str.split(":")[0]) if es_str else 0
                lf = int(lf_str.split(":")[0]) if lf_str else 24
                
                if es + duration <= lf:
                    status = "SCHEDULED"
                    st = f"{es:02d}:00"
                    ed = f"{(es + duration):02d}:00"
                    explanation = f"Scheduled at earliest possible time ({st})"
                else:
                    status = "CONFLICT"
                    st = f"{es:02d}:00"
                    ed = f"{(es + duration):02d}:00"
                    explanation = "Cannot fit duration within time window."
                    
                schedules.append({
                    "load_id": load["id"],
                    "load_name": load["name"],
                    "scheduled_start": st,
                    "scheduled_end": ed,
                    "scheduled_date": date_str,
                    "power_kw": load["power_kw"],
                    "duration_hours": load["duration_hours"],
                    "renewable_available_kw": 0.0,
                    "battery_impact_kwh": 0.0,
                    "status": status,
                    "explanation": explanation,
                    "priority": load.get("priority", "medium")
                })
        return schedules

    def calculate_metrics(self, schedule: List[Dict], forecast_data: List[Dict], battery_config: Dict) -> Dict:
        from .metrics import MetricsCalculator
        calc = MetricsCalculator()
        hourly_gen = [f.get("predicted_generation_kw", 0) for f in forecast_data] if forecast_data else [0]*24
        return calc.calculate_all(schedule, hourly_gen, battery_config)
