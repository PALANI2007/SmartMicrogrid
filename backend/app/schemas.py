from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class SolarDataSchema(BaseModel):
    timestamp: datetime
    solar_generation_kw: float
    temperature: float
    humidity: float
    cloud_cover: float
    wind_speed: float
    hour: int
    day_of_week: int
    month: int
    is_weekend: bool
    model_config = ConfigDict(from_attributes=True)

class LoadBase(BaseModel):
    name: str
    load_type: str
    power_kw: float
    duration_hours: float
    earliest_start: Optional[str] = None
    latest_finish: Optional[str] = None
    priority: str
    is_active: bool = True
    min_comfort_temp: Optional[float] = None
    max_comfort_temp: Optional[float] = None
    description: Optional[str] = None

class LoadCreate(LoadBase):
    pass

class LoadUpdate(LoadBase):
    pass

class LoadResponse(LoadBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BatteryConfigBase(BaseModel):
    capacity_kwh: float
    initial_soc: float
    minimum_soc: float
    maximum_soc: float
    max_charge_kw: float
    max_discharge_kw: float
    charging_efficiency: float
    discharging_efficiency: float
    current_soc: float

class BatteryConfigUpdate(BatteryConfigBase):
    pass

class BatteryConfigResponse(BatteryConfigBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ForecastPoint(BaseModel):
    timestamp: datetime
    predicted_generation_kw: float
    lower_bound_kw: float
    upper_bound_kw: float
    confidence_score: float
    actual_generation_kw: Optional[float] = None
    mae: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class ForecastResponse(BaseModel):
    date: str
    data: List[ForecastPoint]

class ScheduleResponse(BaseModel):
    id: int
    run_id: str
    schedule_type: str
    load_id: int
    load_name: str
    scheduled_start: str
    scheduled_end: str
    scheduled_date: datetime
    power_kw: float
    duration_hours: float
    renewable_available_kw: float
    battery_impact_kwh: float
    status: str
    explanation: str
    priority: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ScheduleRunRequest(BaseModel):
    date_str: Optional[str] = None

class ExperimentRequest(BaseModel):
    date_str: str
    experiment_name: str

class ExperimentResultResponse(BaseModel):
    id: int
    run_id: str
    experiment_name: str
    schedule_type: str
    renewable_self_consumption_pct: float
    renewable_export_kwh: float
    renewable_curtailment_kwh: float
    grid_energy_kwh: float
    battery_charge_kwh: float
    battery_discharge_kwh: float
    flexible_completion_rate: float
    deadline_violations: int
    comfort_violations: int
    essential_interruptions: int
    user_disruption_score: float
    total_renewable_kwh: float
    self_consumed_kwh: float
    created_at: datetime
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class DashboardResponse(BaseModel):
    current_solar_kw: float
    predicted_solar_kw: float
    total_load_kw: float
    essential_load_kw: float
    flexible_load_kw: float
    battery_soc: float
    renewable_self_consumption_pct: float
    renewable_export_kwh: float
    grid_dependency_pct: float
    system_status: str
    active_loads: List[dict]
    hourly_data: List[dict]

class MetricsResponse(BaseModel):
    metrics: dict

class ValidationResponseCreate(BaseModel):
    respondent_name: Optional[str] = None
    q1_understandable: int = Field(ge=1, le=5)
    q2_explanation_clear: int = Field(ge=1, le=5)
    q3_disruption: int = Field(ge=1, le=5)
    q4_easy_to_read: int = Field(ge=1, le=5)
    q5_language_useful: int = Field(ge=1, le=5)
    q6_confidence_clear: int = Field(ge=1, le=5)
    overall_satisfaction: float = Field(ge=1, le=5)
    notes: Optional[str] = None

class ValidationResponseRead(ValidationResponseCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class HealthResponse(BaseModel):
    status: str

class ConflictDetail(BaseModel):
    conflict_reason: str
    details: str

class ExplanationDetail(BaseModel):
    short: str
    detailed: str
    factors: List[dict]
