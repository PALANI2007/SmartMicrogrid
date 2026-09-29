class ConstraintChecker:
    """
    Hard-constraint validator for the greedy scheduler.

    Each public static method encodes a single scheduling rule that *must* be
    satisfied for a proposed time slot to be considered feasible.  Violating any
    one of these constraints causes the slot to be rejected by the scheduler.

    Hard constraints enforced:
    - Loads may not start before their ``earliest_start`` time.
    - Loads must finish by their ``latest_finish`` deadline.
    - The scheduled duration must be at least as long as the required duration.
    - The total simultaneous power draw across all scheduled loads must not exceed
      the site's maximum power capacity (default 15 kW).

    Battery SOC bounds are also exposed as static helpers but are not wired into
    ``check_all_constraints`` because the scheduler tracks SOC externally as a
    scalar approximation (see ``scheduler_engine.py`` for rationale).
    """

    @staticmethod
    def essential_loads_protected(load: dict) -> bool:
        """
        Return True if the load is essential and therefore cannot be time-shifted.

        Essential loads are always scheduled for the full day (00:00–24:00) by
        the scheduler engine; this helper is used by external callers that need
        to check whether a load is shiftable before applying time-window logic.

        Parameters
        ----------
        load : dict
            Load definition dict containing at least ``load_type``.

        Returns
        -------
        bool
            ``True`` if ``load_type == "essential"``, ``False`` otherwise.
        """
        # Essential loads are protected (can't be shifted) if load_type == 'essential'
        return load.get("load_type") == "essential"

    @staticmethod
    def start_not_before(scheduled_start: int, earliest_start: str) -> bool:
        """
        Validate that the proposed start hour respects the load's earliest start.

        Parameters
        ----------
        scheduled_start : int
            Proposed start hour (0–23).
        earliest_start : str
            Earliest allowed start time in ``HH:MM`` format, or ``None`` if
            there is no lower bound.

        Returns
        -------
        bool
            ``True`` if the constraint is satisfied (or not applicable).
        """
        if not earliest_start:
            return True
        es = int(earliest_start.split(":")[0])
        return scheduled_start >= es

    @staticmethod
    def finish_before_deadline(scheduled_end: int, deadline: str) -> bool:
        """
        Validate that the proposed end hour does not exceed the load's deadline.

        Parameters
        ----------
        scheduled_end : int
            Proposed end hour (1–24, exclusive upper bound of the slot).
        deadline : str
            Latest allowed finish time in ``HH:MM`` format, or ``None`` if there
            is no upper bound.

        Returns
        -------
        bool
            ``True`` if the constraint is satisfied (or not applicable).
        """
        if not deadline:
            return True
        dl = int(deadline.split(":")[0])
        return scheduled_end <= dl

    @staticmethod
    def duration_satisfied(duration_scheduled: float, duration_required: float) -> bool:
        """
        Validate that the scheduled slot is long enough to cover the required runtime.

        Parameters
        ----------
        duration_scheduled : float
            Length of the proposed slot in hours (``end_hour - start_hour``).
        duration_required : float
            Minimum required operating time in hours from the load definition.

        Returns
        -------
        bool
            ``True`` if ``duration_scheduled >= duration_required``.
        """
        return duration_scheduled >= duration_required

    @staticmethod
    def battery_soc_valid(soc: float, min_soc: float, max_soc: float) -> bool:
        """
        Check whether the current battery state-of-charge is within allowed bounds.

        Parameters
        ----------
        soc : float
            Current state-of-charge as a fraction (0.0–1.0).
        min_soc : float
            Minimum allowed SOC (e.g., 0.2 to preserve battery longevity).
        max_soc : float
            Maximum allowed SOC (e.g., 0.95 to avoid overcharge).

        Returns
        -------
        bool
            ``True`` if ``min_soc <= soc <= max_soc``.
        """
        return min_soc <= soc <= max_soc

    @staticmethod
    def battery_power_valid(power: float, max_power: float) -> bool:
        """
        Check whether a charge/discharge power request is within the rated limit.

        Parameters
        ----------
        power : float
            Proposed charge (positive) or discharge (negative) power in kW.
        max_power : float
            Maximum allowable absolute power in kW (from battery spec).

        Returns
        -------
        bool
            ``True`` if ``|power| <= max_power``.
        """
        return abs(power) <= max_power

    @staticmethod
    def no_power_overlap(new_start: int, new_end: int, new_power: float, existing_schedules: list, max_power: float = 15.0) -> bool:
        """
        Validate that adding a new load does not breach the site power capacity.

        Builds an hourly power profile from all currently SCHEDULED loads and
        checks whether adding ``new_power`` in the range ``[new_start, new_end)``
        would exceed ``max_power`` in any hour.

        Parameters
        ----------
        new_start : int
            Start hour (0–23) of the proposed load.
        new_end : int
            End hour (1–24, exclusive) of the proposed load.
        new_power : float
            Power draw of the new load (kW).
        existing_schedules : list[dict]
            Schedule entries already committed (must have ``scheduled_start``,
            ``scheduled_end``, ``power_kw``, and ``status``).
        max_power : float, optional
            Site-level power capacity limit in kW. Defaults to 15.0 kW.

        Returns
        -------
        bool
            ``True`` if the site capacity limit is not exceeded in any hour.
        """
        hourly_power = [0.0] * 24
        for s in existing_schedules:
            st = int(s["scheduled_start"].split(":")[0])
            ed = int(s["scheduled_end"].split(":")[0])
            for h in range(st, ed):
                if 0 <= h < 24:
                    hourly_power[h] += s["power_kw"]

        for h in range(new_start, new_end):
            if 0 <= h < 24:
                if hourly_power[h] + new_power > max_power:
                    return False
        return True

    @classmethod
    def check_all_constraints(cls, load: dict, start_hour: int, end_hour: int, battery_soc: float, battery_config: dict, existing_schedules: list) -> dict:
        """
        Run all hard constraints for a proposed (load, slot) combination.

        Checks four hard constraints in order:
        1. ``start_not_before`` — earliest-start time window boundary.
        2. ``finish_before_deadline`` — latest-finish (deadline) boundary.
        3. ``duration_satisfied`` — slot length ≥ required duration.
        4. ``no_power_overlap`` — cumulative site power ≤ 15 kW in every hour.

        Battery SOC constraints are not applied here because the scheduler
        engine tracks SOC as a coarse scalar approximation; a full SOC
        simulation is performed later by ``MetricsCalculator``.

        Parameters
        ----------
        load : dict
            Load definition; relevant keys: ``earliest_start``, ``latest_finish``,
            ``duration_hours``, ``power_kw``.
        start_hour : int
            Proposed start hour (0–23).
        end_hour : int
            Proposed end hour (1–24, exclusive).
        battery_soc : float
            Current battery SOC (carried forward by the scheduler for context,
            not directly checked in this method).
        battery_config : dict
            Battery configuration dict (reserved for future SOC constraint checks).
        existing_schedules : list[dict]
            Already-committed schedule entries used for the power-overlap check.

        Returns
        -------
        dict
            ``{"feasible": bool, "violations": list[str], "warnings": list[str]}``
            ``feasible`` is ``True`` only when ``violations`` is empty.
        """
        violations = []
        warnings = []

        if not cls.start_not_before(start_hour, load.get("earliest_start")):
            violations.append(f"Starts before earliest_start ({load.get('earliest_start')})")

        if not cls.finish_before_deadline(end_hour, load.get("latest_finish")):
            violations.append(f"Finishes after deadline ({load.get('latest_finish')})")

        if not cls.duration_satisfied(end_hour - start_hour, load.get("duration_hours", 0)):
            violations.append("Duration not satisfied")

        if not cls.no_power_overlap(start_hour, end_hour, load.get("power_kw", 0), existing_schedules):
            violations.append("Power overlap exceeds max power capacity")

        feasible = len(violations) == 0
        return {"feasible": feasible, "violations": violations, "warnings": warnings}
