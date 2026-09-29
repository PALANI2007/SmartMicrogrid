from typing import List, Dict
from datetime import datetime
from .constraints import ConstraintChecker


class RenewableAwareScheduler:
    """
    Renewable-aware load scheduler using a greedy priority-weighted heuristic.

    This is NOT a global optimizer (e.g., not ILP or MILP). Instead, it uses a
    deterministic greedy strategy: loads are processed in priority order, and for
    each load the time slot that maximises a composite score (renewable availability,
    priority, battery impact, and scheduling margin) is chosen.

    Because decisions are made greedily and sequentially, earlier/higher-priority
    loads can block slots for later/lower-priority loads, so the result is a
    locally-good but not necessarily globally-optimal schedule.

    Attributes
    ----------
    constraint_checker : ConstraintChecker
        Validates hard constraints (time windows, power limits, battery SOC)
        before a candidate slot is accepted.
    """

    def __init__(self):
        self.constraint_checker = ConstraintChecker()

    def schedule(
        self,
        loads: List[Dict],
        forecast_data: List[Dict],
        battery_config: Dict,
        date_str: str,
    ) -> List[Dict]:
        """
        Produce a day-ahead schedule for a list of loads given solar forecast data.

        Algorithm steps
        ---------------
        1. Separate loads into ``essential`` (always SCHEDULED 00:00–24:00) and
           ``flexible`` (time-shiftable within a user-defined window).
        2. Sort flexible loads by priority (high > medium > low) so that
           higher-priority loads claim the best slots first.
        3. Build an hourly generation lookup from *forecast_data*.
        4. For each flexible load, iterate over every feasible start hour
           ``[earliest_start, latest_finish - duration]``, check hard constraints,
           compute a composite score, and record the best-scoring slot.
        5. If a valid slot is found the load is marked ``SCHEDULED``; otherwise
           it is marked ``CONFLICT``.

        Parameters
        ----------
        loads : list[dict]
            Load definitions. Each dict must contain at minimum: ``id``, ``name``,
            ``load_type``, ``power_kw``, ``duration_hours``, ``priority``,
            ``earliest_start`` (HH:MM), ``latest_finish`` (HH:MM).
        forecast_data : list[dict]
            Hourly solar generation forecast, one entry per hour. Each dict must
            contain ``timestamp`` (ISO-8601 string or datetime) and
            ``predicted_generation_kw``.
        battery_config : dict
            Battery parameters: ``initial_soc``, ``capacity_kwh``, ``minimum_soc``,
            ``maximum_soc``, ``max_charge_kw``, ``max_discharge_kw``,
            ``charging_efficiency``, ``discharging_efficiency``.
        date_str : str
            Target date in ``YYYY-MM-DD`` format, stored on every schedule entry.

        Returns
        -------
        list[dict]
            One schedule entry per load with keys: ``load_id``, ``load_name``,
            ``scheduled_start``, ``scheduled_end``, ``scheduled_date``,
            ``power_kw``, ``duration_hours``, ``renewable_available_kw``,
            ``battery_impact_kwh``, ``status`` (``SCHEDULED`` | ``CONFLICT``),
            ``explanation``, ``priority``.
        """
        schedules = []
        essential_loads = [l for l in loads if l.get("load_type") == "essential"]
        flexible_loads = [l for l in loads if l.get("load_type") == "flexible"]

        # Sort flexible loads by priority (high > medium > low)
        priority_map = {"high": 3, "medium": 2, "low": 1}
        flexible_loads.sort(key=lambda x: priority_map.get(x.get("priority", "low"), 1), reverse=True)

        hourly_gen = {int(f["timestamp"].split("T")[1].split(":")[0]) if isinstance(f["timestamp"], str) else f["timestamp"].hour : f.get("predicted_generation_kw", 0) for f in forecast_data}
        for h in range(24):
            if h not in hourly_gen:
                hourly_gen[h] = 0.0

        # Essential loads always run 00:00–24:00 regardless of solar forecast;
        # they cannot be time-shifted or interrupted.
        for load in essential_loads:
            schedules.append({
                "load_id": load["id"],
                "load_name": load["name"],
                "scheduled_start": "00:00",
                "scheduled_end": "24:00",
                "scheduled_date": date_str,
                "power_kw": load["power_kw"],
                "duration_hours": 24.0,
                "renewable_available_kw": 0.0,
                "battery_impact_kwh": 0.0,
                "status": "SCHEDULED",
                "explanation": "Essential load running continuously.",
                "priority": load.get("priority", "high")
            })

        # Track SOC as a scalar that evolves across the *scheduling* decisions.
        # Because the greedy algorithm processes loads sequentially it uses a single
        # running SOC estimate rather than a full per-hour simulation. This is an
        # approximation: the constraint checker uses this SOC to guard against
        # obvious battery violations at scheduling time; the true post-schedule SOC
        # trajectory is computed precisely by MetricsCalculator after all loads are
        # placed.
        current_soc = battery_config.get("initial_soc", 0.5)

        for load in flexible_loads:
            es_str = load.get("earliest_start")
            lf_str = load.get("latest_finish")
            duration = int(load.get("duration_hours", 1))
            power = load.get("power_kw", 0)

            es = int(es_str.split(":")[0]) if es_str else 0
            lf = int(lf_str.split(":")[0]) if lf_str else 24

            best_score = -9999
            best_slot = None
            best_explanation = ""
            best_impact = 0.0

            for start_h in range(es, lf - duration + 1):
                end_h = start_h + duration

                # Check constraints
                constraints_res = self.constraint_checker.check_all_constraints(load, start_h, end_h, current_soc, battery_config, schedules)
                if not constraints_res["feasible"]:
                    continue

                avg_renewable = sum([hourly_gen[h] for h in range(start_h, end_h)]) / duration if duration > 0 else 0

                # Calculate existing power
                existing_power = 0
                for s in schedules:
                    if s["status"] == "SCHEDULED":
                        st = int(s["scheduled_start"].split(":")[0])
                        ed = int(s["scheduled_end"].split(":")[0])
                        if st <= start_h < ed:
                            existing_power += s["power_kw"]

                surplus = avg_renewable - existing_power - power
                battery_impact = min(0, surplus) * duration # negative if deficit

                # Composite scoring formula — each term represents one objective:
                #   2.0 * avg_renewable  : strongly favour slots with high solar output
                #                          (maximise renewable self-consumption)
                #   1.0 * priority_score : reward higher-priority loads (high=3, medium=2, low=1)
                #   1.5 * (1 - |impact|) : penalise large battery draw; the magnitude
                #                          of battery_impact is negative for deficits
                #                          so (1 - |impact|) decreases as deficit grows
                #   0.5 * time_margin    : mild preference for earlier slots so that
                #                          later hours remain available for other loads
                priority_score = priority_map.get(load.get("priority", "low"), 1)
                time_margin = lf - end_h

                score = (2.0 * avg_renewable) + (1.0 * priority_score) + (1.5 * (1 - abs(battery_impact))) + (0.5 * time_margin)

                if score > best_score:
                    best_score = score
                    best_slot = (start_h, end_h)
                    best_impact = battery_impact
                    best_explanation = self.generate_explanation(load, (start_h, end_h), avg_renewable, battery_impact)

            if best_slot:
                schedules.append({
                    "load_id": load["id"],
                    "load_name": load["name"],
                    "scheduled_start": f"{best_slot[0]:02d}:00",
                    "scheduled_end": f"{best_slot[1]:02d}:00",
                    "scheduled_date": date_str,
                    "power_kw": load["power_kw"],
                    "duration_hours": load["duration_hours"],
                    "renewable_available_kw": sum([hourly_gen[h] for h in range(best_slot[0], best_slot[1])]),
                    "battery_impact_kwh": best_impact,
                    "status": "SCHEDULED",
                    "explanation": best_explanation,
                    "priority": load.get("priority", "medium")
                })
            else:
                # CONFLICT is triggered when either:
                #   (a) the duration exceeds the allowed time window (no valid start
                #       hour exists in range(es, lf - duration + 1)), OR
                #   (b) every candidate slot violates at least one hard constraint
                #       (power cap, battery SOC limit, time-window boundary).
                # The load is still returned so the caller knows it could not be placed.
                schedules.append({
                    "load_id": load["id"],
                    "load_name": load["name"],
                    "scheduled_start": "00:00",
                    "scheduled_end": f"{duration:02d}:00",
                    "scheduled_date": date_str,
                    "power_kw": load["power_kw"],
                    "duration_hours": load["duration_hours"],
                    "renewable_available_kw": 0.0,
                    "battery_impact_kwh": 0.0,
                    "status": "CONFLICT",
                    "explanation": "No feasible time slot found within window matching constraints.",
                    "priority": load.get("priority", "medium")
                })

        return schedules

    def calculate_metrics(self, schedule: List[Dict], forecast_data: List[Dict], battery_config: Dict) -> Dict:
        """
        Compute post-schedule energy and reliability metrics via MetricsCalculator.

        Delegates the full hour-by-hour simulation to ``MetricsCalculator.calculate_all``
        and returns its result unchanged. See ``metrics.MetricsCalculator`` for the
        complete list of returned keys.

        Parameters
        ----------
        schedule : list[dict]
            Output of ``schedule()``; each entry must carry ``status``,
            ``scheduled_start``, ``scheduled_end``, and ``power_kw``.
        forecast_data : list[dict]
            24-entry hourly forecast; ``predicted_generation_kw`` is used.
        battery_config : dict
            Battery configuration dict (same shape as passed to ``schedule()``).

        Returns
        -------
        dict
            Metrics dict from ``MetricsCalculator.calculate_all()``.
        """
        from .metrics import MetricsCalculator
        calc = MetricsCalculator()
        hourly_gen = [f.get("predicted_generation_kw", 0) for f in forecast_data] if forecast_data else [0]*24
        return calc.calculate_all(schedule, hourly_gen, battery_config)

    def generate_explanation(self, load: dict, selected_slot: tuple, avg_renewable: float, battery_impact: float) -> str:
        """
        Build a human-readable explanation string for a scheduled load.

        The explanation tells the end user *why* this particular slot was chosen:
        it surfaces the average solar generation during the window and the
        estimated battery impact so users can understand the scheduling decision.

        Parameters
        ----------
        load : dict
            Load definition dict (must contain ``name``).
        selected_slot : tuple[int, int]
            ``(start_hour, end_hour)`` of the chosen slot (24-h integers).
        avg_renewable : float
            Mean solar generation (kW) across the selected slot.
        battery_impact : float
            Estimated net battery energy change (kWh) for the slot;
            negative values indicate the battery will be discharged.

        Returns
        -------
        str
            A one-sentence explanation suitable for display in the UI.
        """
        start_h, end_h = selected_slot
        return f"{load['name']} scheduled {start_h:02d}:00-{end_h:02d}:00 because solar forecast averages {avg_renewable:.1f} kW during this period with battery impact of {battery_impact:.1f} kWh."
