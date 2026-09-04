from typing import List, Dict
from datetime import datetime
from .constraints import ConstraintChecker

class RenewableAwareScheduler:
    def __init__(self):
        self.constraint_checker = ConstraintChecker()
        
    def schedule(self, loads: List[Dict], forecast_data: List[Dict], battery_config: Dict, date_str: str) -> List[Dict]:
        schedules = []
        essential_loads = [l for l in loads if l.get("load_type") == "essential"]
        flexible_loads = [l for l in loads if l.get("load_type") == "flexible"]
        
        # Sort flexible loads by priority (high > medium > low)
        priority_map = {"high": 3, "medium": 2, "low": 1}
        flexible_loads.sort(key=lambda x: priority_map.get(x.get("priority", "low"), 1), reverse=True)
        
        hourly_gen = {int(f["timestamp"].split("T")[1].split(":")[0]) if isinstance(f["timestamp"], str) else f["timestamp"].hour : f.get("predicted_generation_kw", 0) for f in forecast_data}
        for h in range(24):
            if h not in hourly_gen:
                hourly_gen[h] = 0.0
                
        for load in essential_loads:
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
                "explanation": "Essential load running continuously.",
                "priority": load.get("priority", "high")
            })
            
        current_soc = battery_config.get("initial_soc", 0.5)
        
        for load in flexible_loads:
            es_str = load.get("earliest_start")
            lf_str = load.get("latest_finish")
            duration = int(load.get("duration_hours", 1))
            power = load.get("power_kw", 0)
            
            es = int(es_str.split(":")[0]) if es_str else 0
            lf = int(lf_str.split(":")[0]) if lf_str else 24
            
            best_score = -9999
            best_slot = None
            best_explanation = ""
            best_impact = 0.0
            
            for start_h in range(es, lf - duration + 1):
                end_h = start_h + duration
                
                # Check constraints
                constraints_res = self.constraint_checker.check_all_constraints(load, start_h, end_h, current_soc, battery_config, schedules)
                if not constraints_res["feasible"]:
                    continue
                    
                avg_renewable = sum([hourly_gen[h] for h in range(start_h, end_h)]) / duration if duration > 0 else 0
                
                # Calculate existing power
                existing_power = 0
                for s in schedules:
                    if s["status"] == "SCHEDULED":
                        st = int(s["scheduled_start"].split(":")[0])
                        ed = int(s["scheduled_end"].split(":")[0])
                        if st <= start_h < ed:
                            existing_power += s["power_kw"]
                            
                surplus = avg_renewable - existing_power - power
                battery_impact = min(0, surplus) * duration # negative if deficit
                
                # Scoring
                priority_score = priority_map.get(load.get("priority", "low"), 1)
                time_margin = lf - end_h
                
                score = (2.0 * avg_renewable) + (1.0 * priority_score) + (1.5 * (1 - abs(battery_impact))) + (0.5 * time_margin)
                
                if score > best_score:
                    best_score = score
                    best_slot = (start_h, end_h)
                    best_impact = battery_impact
                    best_explanation = self.generate_explanation(load, (start_h, end_h), avg_renewable, battery_impact)
                    
            if best_slot:
                schedules.append({
                    "load_id": load["id"],
                    "load_name": load["name"],
                    "scheduled_start": f"{best_slot[0]:02d}:00",
                    "scheduled_end": f"{best_slot[1]:02d}:00",
                    "scheduled_date": date_str,
                    "power_kw": load["power_kw"],
                    "duration_hours": load["duration_hours"],
                    "renewable_available_kw": sum([hourly_gen[h] for h in range(best_slot[0], best_slot[1])]),
                    "battery_impact_kwh": best_impact,
                    "status": "SCHEDULED",
                    "explanation": best_explanation,
                    "priority": load.get("priority", "medium")
                })
            else:
                schedules.append({
                    "load_id": load["id"],
                    "load_name": load["name"],
                    "scheduled_start": "00:00",
                    "scheduled_end": f"{duration:02d}:00",
                    "scheduled_date": date_str,
                    "power_kw": load["power_kw"],
                    "duration_hours": load["duration_hours"],
                    "renewable_available_kw": 0.0,
                    "battery_impact_kwh": 0.0,
                    "status": "CONFLICT",
                    "explanation": "No feasible time slot found within window matching constraints.",
                    "priority": load.get("priority", "medium")
                })
                
        return schedules

    def calculate_metrics(self, schedule: List[Dict], forecast_data: List[Dict], battery_config: Dict) -> Dict:
        from .metrics import MetricsCalculator
        calc = MetricsCalculator()
        hourly_gen = [f.get("predicted_generation_kw", 0) for f in forecast_data] if forecast_data else [0]*24
        return calc.calculate_all(schedule, hourly_gen, battery_config)
        
    def generate_explanation(self, load: dict, selected_slot: tuple, avg_renewable: float, battery_impact: float) -> str:
        start_h, end_h = selected_slot
        return f"{load['name']} scheduled {start_h:02d}:00-{end_h:02d}:00 because solar forecast averages {avg_renewable:.1f} kW during this period with battery impact of {battery_impact:.1f} kWh."
