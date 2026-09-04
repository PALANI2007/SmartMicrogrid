from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from .baseline_scheduler import BaselineScheduler
from .scheduler_engine import RenewableAwareScheduler
from ..models import ExperimentResult, Load, BatteryConfig
from ..services.forecast_service import ForecastService

class ExperimentRunner:
    def __init__(self, db: Session):
        self.db = db
        self.baseline = BaselineScheduler()
        self.smart = RenewableAwareScheduler()
        self.forecast_service = ForecastService()

    def run_experiment(self, date_str: str, experiment_name: str) -> Dict:
        """Run both baseline and smart schedulers and return a side-by-side comparison."""
        # 1. Fetch loads and battery config from DB
        loads = [
            {
                "id": l.id,
                "name": l.name,
                "load_type": l.load_type,
                "power_kw": l.power_kw,
                "duration_hours": l.duration_hours,
                "earliest_start": l.earliest_start,
                "latest_finish": l.latest_finish,
                "priority": l.priority
            }
            for l in self.db.query(Load).filter(Load.is_active == True).all()
        ]
        
        battery_db = self.db.query(BatteryConfig).first()
        battery_config = {
            "capacity_kwh": battery_db.capacity_kwh,
            "initial_soc": battery_db.initial_soc,
            "minimum_soc": battery_db.minimum_soc,
            "maximum_soc": battery_db.maximum_soc,
            "max_charge_kw": battery_db.max_charge_kw,
            "max_discharge_kw": battery_db.max_discharge_kw,
            "charging_efficiency": battery_db.charging_efficiency,
            "discharging_efficiency": battery_db.discharging_efficiency,
        } if battery_db else {
            "capacity_kwh": 10.0, "initial_soc": 0.5, "minimum_soc": 0.2, "maximum_soc": 0.95,
            "max_charge_kw": 3.0, "max_discharge_kw": 3.0, "charging_efficiency": 0.95, "discharging_efficiency": 0.95
        }
        
        # 2. Get Forecast Data
        forecast_data = self.forecast_service.get_forecast(self.db, date_str)
        
        # 3. Run Baseline
        baseline_schedule = self.baseline.schedule(loads, date_str)
        baseline_metrics = self.baseline.calculate_metrics(baseline_schedule, forecast_data, battery_config)
        
        # 4. Run Smart Scheduler
        smart_schedule = self.smart.schedule(loads, forecast_data, battery_config, date_str)
        smart_metrics = self.smart.calculate_metrics(smart_schedule, forecast_data, battery_config)
        
        # 5. Save results to DB
        run_id = f"{experiment_name}-{datetime.now().timestamp()}"
        
        base_res = ExperimentResult(
            run_id=run_id,
            experiment_name=experiment_name,
            schedule_type="baseline",
            **baseline_metrics
        )
        smart_res = ExperimentResult(
            run_id=run_id,
            experiment_name=experiment_name,
            schedule_type="optimized",
            **smart_metrics
        )
        
        self.db.add(base_res)
        self.db.add(smart_res)
        self.db.commit()
        
        return {
            "run_id": run_id,
            "date": date_str,
            "baseline": baseline_metrics,
            "optimized": smart_metrics,
            "baseline_schedule": baseline_schedule,
            "optimized_schedule": smart_schedule,
            "improvement": {
                "self_consumption_pct": smart_metrics["renewable_self_consumption_pct"] - baseline_metrics["renewable_self_consumption_pct"],
                "grid_import_kwh": baseline_metrics["grid_energy_kwh"] - smart_metrics["grid_energy_kwh"],
                "curtailment_kwh": baseline_metrics["renewable_curtailment_kwh"] - smart_metrics["renewable_curtailment_kwh"],
                "disruption_score": baseline_metrics["user_disruption_score"] - smart_metrics["user_disruption_score"]
            }
        }
