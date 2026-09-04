class ConstraintChecker:
    @staticmethod
    def essential_loads_protected(load: dict) -> bool:
        # Essential loads are protected (can't be shifted) if load_type == 'essential'
        return load.get("load_type") == "essential"

    @staticmethod
    def start_not_before(scheduled_start: int, earliest_start: str) -> bool:
        if not earliest_start:
            return True
        es = int(earliest_start.split(":")[0])
        return scheduled_start >= es

    @staticmethod
    def finish_before_deadline(scheduled_end: int, deadline: str) -> bool:
        if not deadline:
            return True
        dl = int(deadline.split(":")[0])
        return scheduled_end <= dl

    @staticmethod
    def duration_satisfied(duration_scheduled: float, duration_required: float) -> bool:
        return duration_scheduled >= duration_required

    @staticmethod
    def battery_soc_valid(soc: float, min_soc: float, max_soc: float) -> bool:
        return min_soc <= soc <= max_soc

    @staticmethod
    def battery_power_valid(power: float, max_power: float) -> bool:
        return abs(power) <= max_power

    @staticmethod
    def no_power_overlap(new_start: int, new_end: int, new_power: float, existing_schedules: list, max_power: float = 15.0) -> bool:
        hourly_power = [0.0] * 24
        for s in existing_schedules:
            st = int(s["scheduled_start"].split(":")[0])
            ed = int(s["scheduled_end"].split(":")[0])
            for h in range(st, ed):
                if 0 <= h < 24:
                    hourly_power[h] += s["power_kw"]
                    
        for h in range(new_start, new_end):
            if 0 <= h < 24:
                if hourly_power[h] + new_power > max_power:
                    return False
        return True

    @classmethod
    def check_all_constraints(cls, load: dict, start_hour: int, end_hour: int, battery_soc: float, battery_config: dict, existing_schedules: list) -> dict:
        violations = []
        warnings = []
        
        if not cls.start_not_before(start_hour, load.get("earliest_start")):
            violations.append(f"Starts before earliest_start ({load.get('earliest_start')})")
            
        if not cls.finish_before_deadline(end_hour, load.get("latest_finish")):
            violations.append(f"Finishes after deadline ({load.get('latest_finish')})")
            
        if not cls.duration_satisfied(end_hour - start_hour, load.get("duration_hours", 0)):
            violations.append("Duration not satisfied")
            
        if not cls.no_power_overlap(start_hour, end_hour, load.get("power_kw", 0), existing_schedules):
            violations.append("Power overlap exceeds max power capacity")
            
        feasible = len(violations) == 0
        return {"feasible": feasible, "violations": violations, "warnings": warnings}
