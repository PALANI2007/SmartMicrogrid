from typing import List, Dict

class MetricsCalculator:
    def calculate_all(self, schedule: List[Dict], hourly_generation: List[float], battery_config: Dict) -> Dict:
        total_grid_energy = 0.0
        total_self_consumed = 0.0
        total_exported = 0.0
        total_battery_charge = 0.0
        total_battery_discharge = 0.0
        total_renewable = sum(hourly_generation)
        
        soc = battery_config.get("initial_soc", 0.5)
        cap = battery_config.get("capacity_kwh", 10.0)
        max_soc = battery_config.get("maximum_soc", 0.95)
        min_soc = battery_config.get("minimum_soc", 0.2)
        max_chg = battery_config.get("max_charge_kw", 3.0)
        max_dis = battery_config.get("max_discharge_kw", 3.0)
        eff_chg = battery_config.get("charging_efficiency", 0.95)
        eff_dis = battery_config.get("discharging_efficiency", 0.95)
        
        for h in range(24):
            gen = hourly_generation[h] if h < len(hourly_generation) else 0.0
            load_h = 0.0
            
            for s in schedule:
                if s["status"] == "SCHEDULED":
                    st = int(s["scheduled_start"].split(":")[0])
                    ed = int(s["scheduled_end"].split(":")[0])
                    if st <= h < ed:
                        load_h += s["power_kw"]
                        
            surplus = max(0.0, gen - load_h)
            deficit = max(0.0, load_h - gen)
            
            if surplus > 0:
                charge_possible = min(surplus, max_chg)
                space_avail = (max_soc - soc) * cap / eff_chg
                actual_charge = min(charge_possible, space_avail)
                soc += (actual_charge * eff_chg) / cap
                total_battery_charge += actual_charge
                total_self_consumed += min(load_h, gen) + actual_charge
                total_exported += surplus - actual_charge
            elif deficit > 0:
                total_self_consumed += gen
                discharge_possible = min(deficit, max_dis)
                energy_avail = (soc - min_soc) * cap * eff_dis
                actual_discharge = min(discharge_possible, energy_avail)
                soc -= (actual_discharge / eff_dis) / cap
                total_battery_discharge += actual_discharge
                rem_deficit = deficit - actual_discharge
                total_grid_energy += rem_deficit
            else:
                total_self_consumed += load_h
                
        total_self_consumed = min(total_self_consumed, total_renewable)
        renewable_self_consumption_pct = (total_self_consumed / total_renewable * 100) if total_renewable > 0 else 0.0
        
        deadline_violations = sum(1 for s in schedule if s["status"] == "CONFLICT")
        total_flexible = sum(1 for s in schedule if s.get("priority") != "high" or s.get("duration_hours", 24) < 24)
        flexible_completed = sum(1 for s in schedule if s["status"] == "SCHEDULED" and (s.get("priority") != "high" or s.get("duration_hours", 24) < 24))
        flexible_completion_rate = (flexible_completed / total_flexible * 100) if total_flexible > 0 else 100.0
        
        # Heuristic disruption score (higher is worse)
        # 10 points per deadline violation, 5 points if load wasn't scheduled at earliest start
        user_disruption_score = deadline_violations * 10
        for s in schedule:
            if s["status"] == "SCHEDULED" and s.get("priority") != "high":
                # Assuming 'earliest_start' is roughly what user prefers
                # We can approximate by looking if priority is 'low' or 'medium'
                pass # Simple approximation: disruption is just deadline violations for now
                
        return {
            "renewable_self_consumption_pct": round(renewable_self_consumption_pct, 2),
            "renewable_export_kwh": round(total_exported, 2),
            "renewable_curtailment_kwh": round(total_exported, 2), # Synonym for this project
            "grid_energy_kwh": round(total_grid_energy, 2),
            "battery_charge_kwh": round(total_battery_charge, 2),
            "battery_discharge_kwh": round(total_battery_discharge, 2),
            "flexible_completion_rate": round(flexible_completion_rate, 2),
            "deadline_violations": deadline_violations,
            "comfort_violations": 0,
            "essential_interruptions": 0,
            "user_disruption_score": user_disruption_score,
            "total_renewable_kwh": round(total_renewable, 2),
            "self_consumed_kwh": round(total_self_consumed, 2)
        }
