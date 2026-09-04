from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.battery_service import BatteryService
from ..services.forecast_service import ForecastService
from ..models import Load

router = APIRouter(prefix="/api/battery", tags=["battery"])
battery_service = BatteryService()
forecast_service = ForecastService()


@router.get("")
def get_battery(db: Session = Depends(get_db)):
    config = battery_service.get_config(db)
    status = battery_service.get_battery_status(db)
    config_dict = {c.name: getattr(config, c.name) for c in config.__table__.columns}
    if "updated_at" in config_dict and config_dict["updated_at"]:
        config_dict["updated_at"] = config_dict["updated_at"].isoformat()
    return {**config_dict, **status}


@router.put("")
def update_battery(payload: dict, db: Session = Depends(get_db)):
    config = battery_service.update_config(db, payload)
    config_dict = {c.name: getattr(config, c.name) for c in config.__table__.columns}
    if "updated_at" in config_dict and config_dict["updated_at"]:
        config_dict["updated_at"] = config_dict["updated_at"].isoformat()
    return config_dict


@router.get("/simulation")
def get_simulation(db: Session = Depends(get_db)):
    from datetime import datetime
    config = battery_service.get_config(db)
    b_dict = {c.name: getattr(config, c.name) for c in config.__table__.columns}
    
    loads = db.query(Load).filter(Load.is_active == True).all()
    total_load = sum(l.power_kw for l in loads)
    
    today = datetime.now().strftime("%Y-%m-%d")
    forecast = forecast_service.get_forecast(db, today)
    hourly_gen = [f.get("predicted_generation_kw", 0) for f in forecast]
    hourly_load = [total_load] * 24
    
    sim = battery_service.simulate_battery(hourly_load, hourly_gen, b_dict)
    return {
        "hourly_soc": sim["hourly_soc"],
        "total_charged_kwh": sim["total_charged_kwh"],
        "total_discharged_kwh": sim["total_discharged_kwh"],
        "min_soc_reached": sim["min_soc_reached"],
        "config": {
            "minimum_soc": config.minimum_soc,
            "maximum_soc": config.maximum_soc,
            "capacity_kwh": config.capacity_kwh,
        }
    }
