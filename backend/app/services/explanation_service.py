class ExplanationService:
    def explain_schedule_decision(self, load_name: str, start_hour: int, end_hour: int, renewable_kw: float, surplus_kw: float, battery_soc: float, deadline: str, priority: str) -> dict:
        short = f"{load_name} scheduled during high solar production."
        detailed = f"{load_name} was scheduled between {start_hour:02d}:00 and {end_hour:02d}:00. This time slot was selected because renewable generation is expected to be {renewable_kw:.1f} kW, leaving a surplus of {surplus_kw:.1f} kW."
        factors = [
            {"factor": "Renewable Availability", "value": f"{renewable_kw:.1f} kW", "impact": "positive"},
            {"factor": "Priority", "value": priority, "impact": "neutral"}
        ]
        return {"short": short, "detailed": detailed, "factors": factors}

    def explain_conflict(self, load_name: str, constraint_violated: str, details: str) -> dict:
        return {"short": "Conflict detected.", "detailed": f"{load_name} conflict: {constraint_violated} - {details}", "factors": []}

    def explain_forecast_error(self, predicted: float, actual: float, schedule_impact: str) -> dict:
        return {"short": "Forecast error impact.", "detailed": f"Predicted {predicted} kW vs Actual {actual} kW. Impact: {schedule_impact}", "factors": []}
