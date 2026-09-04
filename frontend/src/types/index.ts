export interface Load {
  id: number;
  name: string;
  load_type: 'essential' | 'flexible';
  power_kw: number;
  duration_hours: number;
  earliest_start?: string;
  latest_finish?: string;
  priority: 'high' | 'medium' | 'low';
  is_active: boolean;
  description?: string;
  created_at: string;
}

export interface LoadCreate {
  name: string;
  load_type: 'essential' | 'flexible';
  power_kw: number;
  duration_hours: number;
  earliest_start?: string;
  latest_finish?: string;
  priority: 'high' | 'medium' | 'low';
  description?: string;
}

export interface BatteryConfig {
  id: number;
  capacity_kwh: number;
  initial_soc: number;
  minimum_soc: number;
  maximum_soc: number;
  max_charge_kw: number;
  max_discharge_kw: number;
  charging_efficiency: number;
  discharging_efficiency: number;
  current_soc: number;
  updated_at: string;
}

export interface ForecastPoint {
  timestamp: string;
  hour: number;
  predicted_generation_kw: number;
  lower_bound_kw: number;
  upper_bound_kw: number;
  confidence_score: number;
  actual_generation_kw?: number;
}

export interface ForecastMetrics {
  mae: number;
  rmse: number;
  r2: number;
  training_samples: number;
  test_samples: number;
}

export interface ScheduleEntry {
  id?: number;
  load_id: number;
  load_name: string;
  load_type: 'essential' | 'flexible';
  scheduled_start: string;
  scheduled_end: string;
  power_kw: number;
  duration_hours: number;
  renewable_available_kw: number;
  battery_impact_kwh: number;
  status: 'SCHEDULED' | 'CONFLICT' | 'SKIPPED';
  explanation: string;
  priority: string;
  deadline?: string;
}

export interface ScheduleResult {
  run_id: string;
  schedule_type: 'baseline' | 'optimized';
  scheduled_date: string;
  schedule: ScheduleEntry[];
  metrics: ScheduleMetrics;
  created_at: string;
}

export interface ScheduleMetrics {
  renewable_self_consumption_pct: number;
  renewable_export_kwh: number;
  renewable_curtailment_kwh: number;
  grid_energy_kwh: number;
  battery_charge_kwh: number;
  battery_discharge_kwh: number;
  flexible_completion_rate: number;
  deadline_violations: number;
  comfort_violations: number;
  essential_interruptions: number;
  total_renewable_kwh: number;
  self_consumed_kwh: number;
  user_disruption_score: number;
}

export interface DashboardData {
  current_solar_kw: number;
  predicted_solar_kw: number;
  total_load_kw: number;
  essential_load_kw: number;
  flexible_load_kw: number;
  battery_soc: number;
  renewable_self_consumption_pct: number;
  renewable_export_kwh: number;
  grid_dependency_pct: number;
  system_status: 'GOOD' | 'WARNING' | 'CONFLICT';
  active_loads: Load[];
  hourly_data: HourlyDataPoint[];
}

export interface HourlyDataPoint {
  hour: number;
  solar_kw: number;
  load_kw: number;
  battery_soc: number;
  grid_kw: number;
  export_kw: number;
}

export interface ExperimentResult {
  run_id: string;
  experiment_name: string;
  baseline: ScheduleMetrics;
  optimized: ScheduleMetrics;
  improvements: Record<string, number>;
  created_at: string;
}

export interface ValidationResponse {
  respondent_name?: string;
  q1_understandable: number;
  q2_explanation_clear: number;
  q3_disruption: number;
  q4_easy_to_read: number;
  q5_language_useful: number;
  q6_confidence_clear: number;
  notes?: string;
}

export interface AlertItem {
  id: string;
  type: 'forecast_error' | 'low_battery' | 'deadline_conflict' | 'load_spike';
  severity: 'warning' | 'critical' | 'info';
  title: string;
  message: string;
  details: string;
  recommendation: string;
  timestamp: string;
  is_active: boolean;
}
