from sqlalchemy.orm import Session
from datetime import datetime
import json
from ..models import Load, Schedule
from .forecast_service import ForecastService
from .battery_service import BatteryService
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from scheduler.scheduler_engine import RenewableAwareScheduler
from scheduler.baseline_scheduler import BaselineScheduler
from ..utils.helpers import generate_run_id

SCHEDULE_FIELDS = {
    "load_id", "load_name", "scheduled_start", "scheduled_end",
    "scheduled_date", "power_kw", "duration_hours", "renewable_available_kw",
    "battery_impact_kwh", "status", "explanation", "priority"
}

def _parse_date(date_str: str) -> datetime:
    """Convert date string YYYY-MM-DD to datetime."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

def _build_schedule_obj(s: dict, run_id: str, schedule_type: str) -> Schedule:
    """Build a Schedule ORM object from a dict, converting types as needed."""
    # Only include fields that exist in the Schedule model
    fields = {k: v for k, v in s.items() if k in SCHEDULE_FIELDS}
    # Convert scheduled_date string to datetime
    if "scheduled_date" in fields and isinstance(fields["scheduled_date"], str):
        fields["scheduled_date"] = _parse_date(fields["scheduled_date"])
    return Schedule(
        **fields,
        run_id=run_id,
        schedule_type=schedule_type,
        created_at=datetime.utcnow()
    )


class SchedulerService:
    def __init__(self):
        self.forecast_service = ForecastService()
        self.battery_service = BatteryService()
        self.smart_scheduler = RenewableAwareScheduler()
        self.baseline_scheduler = BaselineScheduler()

    def _get_battery_dict(self, db: Session) -> dict:
        battery_conf = self.battery_service.get_config(db)
        if battery_conf:
            d = {}
            for col in battery_conf.__table__.columns:
                d[col.name] = getattr(battery_conf, col.name)
            return d
        return {
            "initial_soc": 0.5, "current_soc": 0.5,
            "capacity_kwh": 10.0, "maximum_soc": 0.95, "minimum_soc": 0.2,
            "max_charge_kw": 3.0, "max_discharge_kw": 3.0,
            "charging_efficiency": 0.95, "discharging_efficiency": 0.95
        }

    def run_smart_schedule(self, db: Session, date_str: str, run_id: str) -> dict:
        loads = db.query(Load).filter(Load.is_active == True).all()
        loads_dict = [
            {
                "id": l.id, "name": l.name, "load_type": l.load_type,
                "power_kw": l.power_kw, "duration_hours": l.duration_hours,
                "earliest_start": l.earliest_start, "latest_finish": l.latest_finish,
                "priority": l.priority
            }
            for l in loads
        ]
        forecast = self.forecast_service.get_forecast(db, date_str)
        b_dict = self._get_battery_dict(db)

        schedule = self.smart_scheduler.schedule(loads_dict, forecast, b_dict, date_str)
        metrics = self.smart_scheduler.calculate_metrics(schedule, forecast, b_dict)

        for s in schedule:
            db_s = _build_schedule_obj(s, run_id, "optimized")
            db.add(db_s)
        db.commit()

        return {"schedule": schedule, "metrics": metrics}

    def run_baseline_schedule(self, db: Session, date_str: str, run_id: str) -> dict:
        loads = db.query(Load).filter(Load.is_active == True).all()
        loads_dict = [
            {
                "id": l.id, "name": l.name, "load_type": l.load_type,
                "power_kw": l.power_kw, "duration_hours": l.duration_hours,
                "earliest_start": l.earliest_start, "latest_finish": l.latest_finish,
                "priority": l.priority
            }
            for l in loads
        ]
        forecast = self.forecast_service.get_forecast(db, date_str)
        b_dict = self._get_battery_dict(db)

        schedule = self.baseline_scheduler.schedule(loads_dict, date_str)
        metrics = self.baseline_scheduler.calculate_metrics(schedule, forecast, b_dict)

        for s in schedule:
            db_s = _build_schedule_obj(s, run_id, "baseline")
            db.add(db_s)
        db.commit()

        return {"schedule": schedule, "metrics": metrics}

    def get_latest_schedule(self, db: Session, schedule_type: str) -> dict:
        latest = (
            db.query(Schedule)
            .filter(Schedule.schedule_type == schedule_type)
            .order_by(Schedule.created_at.desc())
            .first()
        )
        if not latest:
            return {"schedule": [], "metrics": {}}
        run_id = latest.run_id
        schedules = db.query(Schedule).filter(Schedule.run_id == run_id).all()

        s_list = []
        for s in schedules:
            s_dict = {c.name: getattr(s, c.name) for c in s.__table__.columns}
            s_dict["scheduled_date"] = s.scheduled_date.isoformat() if s.scheduled_date else None
            s_dict["created_at"] = s.created_at.isoformat() if s.created_at else None
            s_list.append(s_dict)
            
        # Calculate metrics dynamically
        date_str = s_list[0]["scheduled_date"][:10] if s_list and s_list[0].get("scheduled_date") else datetime.now().strftime("%Y-%m-%d")
        forecast = self.forecast_service.get_forecast(db, date_str)
        b_dict = self._get_battery_dict(db)
        
        if schedule_type == "optimized":
            metrics = self.smart_scheduler.calculate_metrics(s_list, forecast, b_dict)
        else:
            metrics = self.baseline_scheduler.calculate_metrics(s_list, forecast, b_dict)
            
        return {"schedule": s_list, "run_id": run_id, "metrics": metrics}

