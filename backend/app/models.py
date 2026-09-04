from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from datetime import datetime
from .database import Base

class SolarData(Base):
    __tablename__ = "solar_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    solar_generation_kw = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    cloud_cover = Column(Float)
    wind_speed = Column(Float)
    hour = Column(Integer)
    day_of_week = Column(Integer)
    month = Column(Integer)
    is_weekend = Column(Boolean)

class Load(Base):
    __tablename__ = "loads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    load_type = Column(String) # 'essential'/'flexible'
    power_kw = Column(Float)
    duration_hours = Column(Float)
    earliest_start = Column(String, nullable=True)
    latest_finish = Column(String, nullable=True)
    priority = Column(String) # 'high'/'medium'/'low'
    is_active = Column(Boolean, default=True)
    min_comfort_temp = Column(Float, nullable=True)
    max_comfort_temp = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BatteryConfig(Base):
    __tablename__ = "battery_config"
    id = Column(Integer, primary_key=True, index=True)
    capacity_kwh = Column(Float)
    initial_soc = Column(Float)
    minimum_soc = Column(Float)
    maximum_soc = Column(Float)
    max_charge_kw = Column(Float)
    max_discharge_kw = Column(Float)
    charging_efficiency = Column(Float)
    discharging_efficiency = Column(Float)
    current_soc = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    predicted_generation_kw = Column(Float)
    lower_bound_kw = Column(Float)
    upper_bound_kw = Column(Float)
    confidence_score = Column(Float)
    actual_generation_kw = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    schedule_type = Column(String) # 'baseline'/'optimized'
    load_id = Column(Integer, ForeignKey("loads.id"))
    load_name = Column(String)
    scheduled_start = Column(String)
    scheduled_end = Column(String)
    scheduled_date = Column(DateTime)
    power_kw = Column(Float)
    duration_hours = Column(Float)
    renewable_available_kw = Column(Float)
    battery_impact_kwh = Column(Float)
    status = Column(String) # 'SCHEDULED'/'CONFLICT'/'SKIPPED'
    explanation = Column(Text)
    priority = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExperimentResult(Base):
    __tablename__ = "experiment_results"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    experiment_name = Column(String)
    schedule_type = Column(String)
    renewable_self_consumption_pct = Column(Float)
    renewable_export_kwh = Column(Float)
    renewable_curtailment_kwh = Column(Float)
    grid_energy_kwh = Column(Float)
    battery_charge_kwh = Column(Float)
    battery_discharge_kwh = Column(Float)
    flexible_completion_rate = Column(Float)
    deadline_violations = Column(Integer)
    comfort_violations = Column(Integer)
    essential_interruptions = Column(Integer)
    user_disruption_score = Column(Float)
    total_renewable_kwh = Column(Float)
    self_consumed_kwh = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

class ValidationResponse(Base):
    __tablename__ = "validation_responses"
    id = Column(Integer, primary_key=True, index=True)
    respondent_name = Column(String, nullable=True)
    q1_understandable = Column(Integer)
    q2_explanation_clear = Column(Integer)
    q3_disruption = Column(Integer)
    q4_easy_to_read = Column(Integer)
    q5_language_useful = Column(Integer)
    q6_confidence_clear = Column(Integer)
    overall_satisfaction = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
