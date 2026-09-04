from sqlalchemy.orm import Session
from datetime import datetime
from ..models import BatteryConfig


class BatteryService:
    def get_config(self, db: Session) -> BatteryConfig:
        config = db.query(BatteryConfig).first()
        if not config:
            # Create default
            config = BatteryConfig(
                capacity_kwh=10.0, initial_soc=0.5, minimum_soc=0.2,
                maximum_soc=0.95, max_charge_kw=3.0, max_discharge_kw=3.0,
                charging_efficiency=0.95, discharging_efficiency=0.95,
                current_soc=0.5, updated_at=datetime.utcnow()
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config

    def update_config(self, db: Session, config_data: dict) -> BatteryConfig:
        config = self.get_config(db)
        for key, val in config_data.items():
            if hasattr(config, key):
                setattr(config, key, val)
        config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(config)
        return config

    def get_battery_status(self, db: Session) -> dict:
        config = self.get_config(db)
        soc = config.current_soc
        available_kwh = (soc - config.minimum_soc) * config.capacity_kwh
        if soc > 0.9:
            status = "Nearly Full"
        elif soc > 0.6:
            status = "Good"
        elif soc > 0.3:
            status = "Low"
        else:
            status = "Critical"
        return {
            "current_soc": soc,
            "available_kwh": round(max(0, available_kwh), 2),
            "status": status,
            "capacity_kwh": config.capacity_kwh,
        }

    def simulate_battery(self, hourly_load: list, hourly_generation: list, config: dict) -> dict:
        soc = config.get("initial_soc", 0.5)
        capacity = config.get("capacity_kwh", 10.0)
        min_soc = config.get("minimum_soc", 0.2)
        max_soc = config.get("maximum_soc", 0.95)
        max_charge = config.get("max_charge_kw", 3.0)
        max_discharge = config.get("max_discharge_kw", 3.0)
        charge_eff = config.get("charging_efficiency", 0.95)
        discharge_eff = config.get("discharging_efficiency", 0.95)

        hourly_soc = []
        total_charged = 0.0
        total_discharged = 0.0
        min_reached = soc

        for h in range(24):
            gen = hourly_generation[h] if h < len(hourly_generation) else 0
            load = hourly_load[h] if h < len(hourly_load) else 0
            surplus = gen - load

            if surplus > 0:
                charge_kwh = min(surplus, max_charge, (max_soc - soc) * capacity)
                charge_kwh = max(0, charge_kwh)
                soc = min(max_soc, soc + (charge_kwh * charge_eff) / capacity)
                total_charged += charge_kwh
            else:
                deficit = -surplus
                discharge_kwh = min(deficit, max_discharge, (soc - min_soc) * capacity)
                discharge_kwh = max(0, discharge_kwh)
                soc = max(min_soc, soc - discharge_kwh / (capacity * discharge_eff))
                total_discharged += discharge_kwh

            min_reached = min(min_reached, soc)
            hourly_soc.append(round(soc, 4))

        return {
            "hourly_soc": hourly_soc,
            "total_charged_kwh": round(total_charged, 3),
            "total_discharged_kwh": round(total_discharged, 3),
            "min_soc_reached": round(min_reached, 4),
        }
