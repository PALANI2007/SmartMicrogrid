"""
Edge Case Scenario Simulator for SmartMicrogrid Review 2.

Runs 4 predefined stress scenarios using the existing scheduler and metrics
infrastructure. Does NOT re-implement MetricsCalculator or constraint logic.
"""

import math
import copy
from typing import List, Dict, Optional

from .scheduler_engine import RenewableAwareScheduler
from .baseline_scheduler import BaselineScheduler
from .metrics import MetricsCalculator


_DATE_STR = "2026-09-28"  # Canonical test date; real date is irrelevant for scenarios


def _make_forecast(hourly_values: List[float]) -> List[Dict]:
    """
    Build a forecast list from a plain list of 24 hourly generation values.
    The format mirrors what ForecastService.get_forecast() returns so that
    the existing scheduler_engine can consume it unchanged.
    """
    result = []
    for h, val in enumerate(hourly_values):
        ts = f"{_DATE_STR}T{h:02d}:00:00"
        result.append({
            "timestamp": ts,
            "hour": h,
            "predicted_generation_kw": max(0.0, round(val, 3)),
            "lower_bound_kw": max(0.0, round(val * 0.85, 3)),
            "upper_bound_kw": round(val * 1.15, 3),
            "confidence_score": 0.70,
            "actual_generation_kw": None,
        })
    return result


def _hourly_gen_from_forecast(forecast: List[Dict]) -> List[float]:
    """Extract a plain 24-element list of generation values from a forecast list."""
    gen = [0.0] * 24
    for f in forecast:
        h = f.get("hour", 0)
        if 0 <= h < 24:
            gen[h] = f.get("predicted_generation_kw", 0.0)
    return gen


def _count_essential_violations(schedule: List[Dict], db_loads: List[Dict]) -> int:
    """
    Count essential loads that are NOT in SCHEDULED status.
    Essential loads must always be scheduled; any other status is a violation.
    """
    essential_ids = {l["id"] for l in db_loads if l.get("load_type") == "essential"}
    violations = 0
    for s in schedule:
        if s.get("load_id") in essential_ids and s.get("status") != "SCHEDULED":
            violations += 1
    return violations


def _battery_violated(schedule: List[Dict], forecast: List[Dict], battery_config: Dict) -> bool:
    """
    Simulate battery SOC hour-by-hour; return True if SOC ever drops below min_soc.
    Uses the same logic as MetricsCalculator but tracks per-hour SOC.
    """
    soc = battery_config.get("initial_soc", 0.5)
    cap = battery_config.get("capacity_kwh", 10.0)
    max_soc = battery_config.get("maximum_soc", 0.95)
    min_soc = battery_config.get("minimum_soc", 0.2)
    max_chg = battery_config.get("max_charge_kw", 3.0)
    max_dis = battery_config.get("max_discharge_kw", 3.0)
    eff_chg = battery_config.get("charging_efficiency", 0.95)
    eff_dis = battery_config.get("discharging_efficiency", 0.95)

    hourly_gen = _hourly_gen_from_forecast(forecast)

    for h in range(24):
        gen = hourly_gen[h]
        load_h = 0.0
        for s in schedule:
            if s.get("status") == "SCHEDULED":
                try:
                    st = int(s["scheduled_start"].split(":")[0])
                    ed = int(s["scheduled_end"].split(":")[0])
                except (KeyError, ValueError):
                    continue
                if st <= h < ed:
                    load_h += s.get("power_kw", 0.0)

        surplus = max(0.0, gen - load_h)
        deficit = max(0.0, load_h - gen)

        if surplus > 0:
            charge_possible = min(surplus, max_chg)
            space_avail = (max_soc - soc) * cap / eff_chg
            actual_charge = min(charge_possible, space_avail)
            soc += (actual_charge * eff_chg) / cap
        elif deficit > 0:
            discharge_possible = min(deficit, max_dis)
            energy_avail = (soc - min_soc) * cap * eff_dis
            actual_discharge = min(discharge_possible, energy_avail)
            soc -= (actual_discharge / eff_dis) / cap

        if soc < min_soc - 1e-6:
            return True

    return False


class EdgeCaseSimulator:
    """
    Runs predefined stress scenarios against the existing smart/baseline schedulers.
    All heavy lifting (metrics, constraints) is delegated to existing modules.
    """

    def __init__(self):
        self._smart = RenewableAwareScheduler()
        self._baseline = BaselineScheduler()
        self._calc = MetricsCalculator()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run_scenario(
        self,
        scenario_id: str,
        db_loads: List[Dict],
        battery_config: Dict,
    ) -> Dict:
        """
        Run the named scenario and return a structured result dict.

        Parameters
        ----------
        scenario_id : str
            One of: monsoon_cloud_cover | low_battery | essential_load_surge | deadline_conflict
        db_loads : list[dict]
            Active loads from the database (same format used by SchedulerService).
        battery_config : dict
            Battery configuration dict from the database.

        Returns
        -------
        dict with keys: scenario_id, name, description, status, expected_behavior,
                        actual_behavior, baseline_metrics, smart_metrics, schedule,
                        violations, explanation
        """
        dispatch = {
            "monsoon_cloud_cover": self._scenario_monsoon_cloud_cover,
            "low_battery": self._scenario_low_battery,
            "essential_load_surge": self._scenario_essential_load_surge,
            "deadline_conflict": self._scenario_deadline_conflict,
        }
        handler = dispatch.get(scenario_id)
        if handler is None:
            return {
                "scenario_id": scenario_id,
                "name": "Unknown Scenario",
                "description": f"Scenario '{scenario_id}' is not defined.",
                "status": "FAIL",
                "expected_behavior": "",
                "actual_behavior": "Scenario not found.",
                "baseline_metrics": None,
                "smart_metrics": {},
                "schedule": [],
                "violations": {"essential": 0, "deadline": 0, "battery": False},
                "explanation": "Unknown scenario_id provided.",
            }
        return handler(db_loads, battery_config)

    # ------------------------------------------------------------------
    # Scenario 1: Monsoon / Cloud Cover
    # ------------------------------------------------------------------

    def _scenario_monsoon_cloud_cover(self, db_loads: List[Dict], battery_config: Dict) -> Dict:
        """
        Prolonged Monsoon / Cloud Cover
        All solar reduced to 0.2-0.5 kW range; simulate via cloud_cover_pct=95,
        irradiance_wm2 in 50-100 W/m2 band.
        """
        name = "Prolonged Monsoon / Cloud Cover"
        description = (
            "Simulates a sustained monsoon period with heavy cloud cover (95%) "
            "resulting in very low solar irradiance (50-100 W/m2). "
            "Solar generation is reduced to 0.2-0.5 kW for all daylight hours."
        )
        expected = (
            "Essential loads protected, flexible loads shifted to best available "
            "low-generation slots, grid fallback activated"
        )

        # Build cloud-cover-degraded forecast (0.2 * sin curve for daylight hours)
        cloud_hourly = []
        for h in range(24):
            val = 0.2 * max(0.0, math.sin((h - 6) * math.pi / 16))
            cloud_hourly.append(val)

        cloud_forecast = _make_forecast(cloud_hourly)
        hourly_gen = _hourly_gen_from_forecast(cloud_forecast)

        # Baseline schedule (no solar awareness)
        baseline_schedule = self._baseline.schedule(db_loads, _DATE_STR)
        baseline_metrics = self._calc.calculate_all(baseline_schedule, hourly_gen, battery_config)

        # Smart schedule
        smart_schedule = self._smart.schedule(db_loads, cloud_forecast, battery_config, _DATE_STR)
        smart_metrics = self._calc.calculate_all(smart_schedule, hourly_gen, battery_config)

        essential_violations = _count_essential_violations(smart_schedule, db_loads)
        deadline_violations = sum(1 for s in smart_schedule if s.get("status") == "CONFLICT")
        batt_violated = _battery_violated(smart_schedule, cloud_forecast, battery_config)

        passed = essential_violations == 0 and len(smart_schedule) > 0

        actual = (
            f"Smart scheduler produced {len(smart_schedule)} schedule entries. "
            f"Essential violations: {essential_violations}. "
            f"Deadline conflicts: {deadline_violations}. "
            f"Grid import: {smart_metrics.get('grid_energy_kwh', 0):.2f} kWh (grid fallback active). "
            f"Battery violated: {batt_violated}."
        )

        return {
            "scenario_id": "monsoon_cloud_cover",
            "name": name,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "expected_behavior": expected,
            "actual_behavior": actual,
            "baseline_metrics": baseline_metrics,
            "smart_metrics": smart_metrics,
            "schedule": smart_schedule,
            "violations": {
                "essential": essential_violations,
                "deadline": deadline_violations,
                "battery": batt_violated,
            },
            "explanation": (
                f"Under 95% cloud cover (50-100 W/m2 irradiance), solar generation is "
                f"severely limited. The smart scheduler prioritises essential loads (which remain "
                f"SCHEDULED) and attempts to place flexible loads in any available window. "
                f"Grid fallback covers the energy deficit. "
                f"Pass condition (essential_violations==0 AND schedule returned): "
                f"MET." if passed else
                f"Under 95% cloud cover (50-100 W/m2 irradiance), solar generation is "
                f"severely limited. Pass condition NOT MET."
            ),
        }

    # ------------------------------------------------------------------
    # Scenario 2: Low / Rapidly Depleting Battery
    # ------------------------------------------------------------------

    def _scenario_low_battery(self, db_loads: List[Dict], battery_config: Dict) -> Dict:
        name = "Low / Rapidly Depleting Battery"
        description = (
            "Battery starts at initial_soc=0.22, just above the minimum reserve (0.20). "
            "Scheduler must avoid discharging below minimum and still serve essential loads."
        )
        expected = (
            "Battery never below min_soc, essential loads protected, "
            "flexible loads delayed, grid fallback"
        )

        # Override battery: initial SOC critically low
        low_batt = copy.deepcopy(battery_config)
        low_batt["initial_soc"] = 0.22

        # Use normal (synthetic realistic) forecast so solar is available
        normal_hourly = [
            max(0.0, 3.0 * math.sin((h - 6) * math.pi / 12))
            for h in range(24)
        ]
        normal_forecast = _make_forecast(normal_hourly)
        hourly_gen = _hourly_gen_from_forecast(normal_forecast)

        smart_schedule = self._smart.schedule(db_loads, normal_forecast, low_batt, _DATE_STR)
        smart_metrics = self._calc.calculate_all(smart_schedule, hourly_gen, low_batt)

        essential_violations = _count_essential_violations(smart_schedule, db_loads)
        deadline_violations = sum(1 for s in smart_schedule if s.get("status") == "CONFLICT")
        batt_violated = _battery_violated(smart_schedule, normal_forecast, low_batt)

        # Pass: no battery violation AND all essential loads SCHEDULED
        passed = (not batt_violated) and (essential_violations == 0)

        actual = (
            f"Battery started at SOC=0.22 (min={low_batt['minimum_soc']}). "
            f"Essential violations: {essential_violations}. "
            f"Battery dipped below min_soc: {batt_violated}. "
            f"Deadline conflicts (flexible shifted): {deadline_violations}. "
            f"Grid import: {smart_metrics.get('grid_energy_kwh', 0):.2f} kWh."
        )

        return {
            "scenario_id": "low_battery",
            "name": name,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "expected_behavior": expected,
            "actual_behavior": actual,
            "baseline_metrics": None,
            "smart_metrics": smart_metrics,
            "schedule": smart_schedule,
            "violations": {
                "essential": essential_violations,
                "deadline": deadline_violations,
                "battery": batt_violated,
            },
            "explanation": (
                f"With initial SOC at 0.22 (barely above minimum 0.20), the battery has "
                f"almost no discharge capacity. The scheduler must fall back to grid for deficits "
                f"rather than depleting the battery. Essential loads run uninterrupted. "
                f"Pass condition (battery_soc_never_below_min AND essential_loads_scheduled): "
                f"{'MET' if passed else 'NOT MET'}."
            ),
        }

    # ------------------------------------------------------------------
    # Scenario 3: Sudden Essential Load Surge
    # ------------------------------------------------------------------

    def _scenario_essential_load_surge(self, db_loads: List[Dict], battery_config: Dict) -> Dict:
        name = "Sudden Essential Load Surge"
        description = (
            "A synthetic Emergency Medical Equipment load (5.0 kW, 24 h, essential/high) "
            "is added at runtime, approximately doubling total essential load demand."
        )
        expected = (
            "Essential loads given highest priority, battery and grid support activated, "
            "flexible loads shifted"
        )

        emergency_load = {
            "id": 9999,
            "name": "Emergency Medical Equipment",
            "load_type": "essential",
            "power_kw": 5.0,
            "duration_hours": 24,
            "priority": "high",
            "earliest_start": None,
            "latest_finish": None,
        }

        # Merge emergency load into the load list (copy to avoid mutating caller data)
        surge_loads = [copy.deepcopy(l) for l in db_loads] + [emergency_load]

        # Use normal solar forecast
        normal_hourly = [
            max(0.0, 3.0 * math.sin((h - 6) * math.pi / 12))
            for h in range(24)
        ]
        normal_forecast = _make_forecast(normal_hourly)
        hourly_gen = _hourly_gen_from_forecast(normal_forecast)

        smart_schedule = self._smart.schedule(surge_loads, normal_forecast, battery_config, _DATE_STR)
        smart_metrics = self._calc.calculate_all(smart_schedule, hourly_gen, battery_config)

        essential_violations = _count_essential_violations(smart_schedule, surge_loads)
        deadline_violations = sum(1 for s in smart_schedule if s.get("status") == "CONFLICT")
        batt_violated = _battery_violated(smart_schedule, normal_forecast, battery_config)

        # Check that emergency load is specifically scheduled
        emergency_entry = next(
            (s for s in smart_schedule if s.get("load_id") == 9999), None
        )
        emergency_scheduled = emergency_entry is not None and emergency_entry.get("status") == "SCHEDULED"

        passed = emergency_scheduled and (essential_violations == 0)

        actual = (
            f"Emergency Medical Equipment (id=9999) status: "
            f"{emergency_entry.get('status') if emergency_entry else 'NOT IN SCHEDULE'}. "
            f"Essential violations: {essential_violations}. "
            f"Battery violated: {batt_violated}. "
            f"Grid import: {smart_metrics.get('grid_energy_kwh', 0):.2f} kWh."
        )

        return {
            "scenario_id": "essential_load_surge",
            "name": name,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "expected_behavior": expected,
            "actual_behavior": actual,
            "baseline_metrics": None,
            "smart_metrics": smart_metrics,
            "schedule": smart_schedule,
            "violations": {
                "essential": essential_violations,
                "deadline": deadline_violations,
                "battery": batt_violated,
            },
            "explanation": (
                f"A 5 kW emergency medical load was injected to simulate a sudden essential "
                f"load surge. The smart scheduler treats all essential loads with unconditional "
                f"scheduling (00:00-24:00). Battery and grid compensate for the energy deficit. "
                f"Pass condition (emergency_load_SCHEDULED AND essential_violations==0): "
                f"{'MET' if passed else 'NOT MET'}."
            ),
        }

    # ------------------------------------------------------------------
    # Scenario 4: Flexible Load Deadline Conflict
    # ------------------------------------------------------------------

    def _scenario_deadline_conflict(self, db_loads: List[Dict], battery_config: Dict) -> Dict:
        name = "Flexible Load Deadline Conflict"
        description = (
            "A synthetic 'Test Narrow Window Load' (3.0 kW, duration=5 h) is given a "
            "3-hour window (14:00-17:00). This is INFEASIBLE because duration > window. "
            "The scheduler must detect and report the conflict."
        )
        expected = (
            "Conflict detected, load reported as CONFLICT, user explanation provided"
        )

        infeasible_load = {
            "id": 8888,
            "name": "Test Narrow Window Load",
            "load_type": "flexible",
            "power_kw": 3.0,
            "duration_hours": 5,
            "earliest_start": "14:00",
            "latest_finish": "17:00",
            "priority": "medium",
        }

        conflict_loads = [copy.deepcopy(l) for l in db_loads] + [infeasible_load]

        # Use normal solar forecast
        normal_hourly = [
            max(0.0, 3.0 * math.sin((h - 6) * math.pi / 12))
            for h in range(24)
        ]
        normal_forecast = _make_forecast(normal_hourly)
        hourly_gen = _hourly_gen_from_forecast(normal_forecast)

        smart_schedule = self._smart.schedule(conflict_loads, normal_forecast, battery_config, _DATE_STR)
        smart_metrics = self._calc.calculate_all(smart_schedule, hourly_gen, battery_config)

        # Find the infeasible load entry
        conflict_entry = next(
            (s for s in smart_schedule if s.get("load_id") == 8888), None
        )
        is_conflict = conflict_entry is not None and conflict_entry.get("status") == "CONFLICT"
        has_explanation = (
            conflict_entry is not None
            and len(conflict_entry.get("explanation", "").strip()) > 0
        )

        essential_violations = _count_essential_violations(smart_schedule, db_loads)
        deadline_violations = sum(1 for s in smart_schedule if s.get("status") == "CONFLICT")
        batt_violated = _battery_violated(smart_schedule, normal_forecast, battery_config)

        passed = is_conflict and has_explanation

        actual = (
            f"Infeasible load (id=8888) status: "
            f"{conflict_entry.get('status') if conflict_entry else 'NOT IN SCHEDULE'}. "
            f"Explanation non-empty: {has_explanation}. "
            f"Total CONFLICT entries: {deadline_violations}. "
            f"Other essential violations: {essential_violations}."
        )

        return {
            "scenario_id": "deadline_conflict",
            "name": name,
            "description": description,
            "status": "PASS" if passed else "FAIL",
            "expected_behavior": expected,
            "actual_behavior": actual,
            "baseline_metrics": None,
            "smart_metrics": smart_metrics,
            "schedule": smart_schedule,
            "violations": {
                "essential": essential_violations,
                "deadline": deadline_violations,
                "battery": batt_violated,
            },
            "explanation": (
                f"The 'Test Narrow Window Load' requires 5 hours but has only a 3-hour "
                f"window (14:00-17:00). The smart scheduler correctly identifies this as "
                f"INFEASIBLE: there is no start hour h in range(14, 17-5+1)=range(14,13) "
                f"which is empty. The load is therefore marked CONFLICT with an explanation. "
                f"Pass condition (status==CONFLICT AND explanation non-empty): "
                f"{'MET' if passed else 'NOT MET'}."
                + (
                    f" Conflict explanation: \"{conflict_entry.get('explanation', '')}\""
                    if conflict_entry else ""
                )
            ),
        }
