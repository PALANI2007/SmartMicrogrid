from typing import List, Dict


class MetricsCalculator:
    """
    Post-schedule energy metrics calculator using an hour-by-hour power flow simulation.

    The calculator steps through each of the 24 hours of a scheduled day and
    applies a simplified but physically-consistent dispatch model:

    1. Compute the scheduled load demand for the hour (sum of all ``SCHEDULED``
       entries that are active in that hour).
    2. Compare generation to demand:
       - **Surplus** (gen > load): excess energy is first offered to the battery
         (respecting charge rate and SOC headroom), then any remainder is counted
         as export/curtailment.
       - **Deficit** (load > gen): the battery discharges up to its rate and SOC
         floor to cover the gap; any remaining deficit is drawn from the grid.
       - **Balance** (gen == load): all renewable energy is self-consumed.
    3. After iterating all 24 hours, aggregate the hourly values into the summary
       metrics returned by ``calculate_all()``.

    This is a *deterministic* simulation — it uses the scheduled start/end times
    verbatim rather than trying to optimise dispatch order. It is therefore best
    treated as a post-hoc accounting tool rather than an online control algorithm.
    """

    def calculate_all(self, schedule: List[Dict], hourly_generation: List[float], battery_config: Dict) -> Dict:
        """
        Simulate power flows for a full 24-hour day and return aggregated metrics.

        The simulation processes hours 0–23 in order. Battery state-of-charge (SOC)
        is carried forward between hours so that charging in sunny hours increases
        the reserve available for evening/night deficits.

        Parameters
        ----------
        schedule : list[dict]
            Output of a scheduler's ``schedule()`` call. Only entries with
            ``status == "SCHEDULED"`` contribute load to the simulation.
            Each entry must have ``scheduled_start`` (HH:MM), ``scheduled_end``
            (HH:MM), and ``power_kw``.
        hourly_generation : list[float]
            24-element list of solar generation values (kW) indexed by hour.
            Values beyond index 23 are ignored; missing hours default to 0.0.
        battery_config : dict
            Battery parameters used for the dispatch simulation:
            ``initial_soc``, ``capacity_kwh``, ``maximum_soc``, ``minimum_soc``,
            ``max_charge_kw``, ``max_discharge_kw``,
            ``charging_efficiency``, ``discharging_efficiency``.

        Returns
        -------
        dict
            Keys and their meanings:

            ``renewable_self_consumption_pct``
                Percentage of total daily renewable generation that was consumed
                on-site (including battery charging from surplus).
            ``renewable_export_kwh``
                Energy exported to the grid (surplus after battery charging, kWh).
            ``renewable_curtailment_kwh``
                Synonym for ``renewable_export_kwh`` in this project (exported
                energy that could not be stored or consumed locally).
            ``grid_energy_kwh``
                Energy drawn from the grid to cover deficits not met by the
                battery (kWh).
            ``battery_charge_kwh``
                Total energy delivered *to* the battery over the day (kWh,
                before charging-efficiency losses).
            ``battery_discharge_kwh``
                Total energy delivered *from* the battery over the day (kWh,
                after discharging-efficiency derating).
            ``flexible_completion_rate``
                Percentage of flexible loads that were successfully scheduled
                (status == ``SCHEDULED``).
            ``deadline_violations``
                Count of schedule entries with status == ``CONFLICT``.
            ``comfort_violations``
                Always 0 in the current implementation (placeholder for future
                comfort-preference tracking).
            ``essential_interruptions``
                Always 0 (essential loads are guaranteed continuous by design).
            ``user_disruption_score``
                Heuristic disruption score (10 points per deadline violation).
                Higher is worse.
            ``total_renewable_kwh``
                Sum of all hourly generation values (kWh).
            ``self_consumed_kwh``
                Absolute kWh of renewable energy consumed on-site (numerator of
                ``renewable_self_consumption_pct``).
        """
        total_grid_energy = 0.0
        total_self_consumed = 0.0
        total_exported = 0.0
        total_battery_charge = 0.0
        total_battery_discharge = 0.0
        total_renewable = sum(hourly_generation)

        soc = battery_config.get("initial_soc", 0.5)
        cap = battery_config.get("capacity_kwh", 10.0)
        max_soc = battery_config.get("maximum_soc", 0.95)
        min_soc = battery_config.get("minimum_soc", 0.2)
        max_chg = battery_config.get("max_charge_kw", 3.0)
        max_dis = battery_config.get("max_discharge_kw", 3.0)
        eff_chg = battery_config.get("charging_efficiency", 0.95)
        eff_dis = battery_config.get("discharging_efficiency", 0.95)

        for h in range(24):
            gen = hourly_generation[h] if h < len(hourly_generation) else 0.0
            load_h = 0.0

            for s in schedule:
                if s["status"] == "SCHEDULED":
                    st = int(s["scheduled_start"].split(":")[0])
                    ed = int(s["scheduled_end"].split(":")[0])
                    if st <= h < ed:
                        load_h += s["power_kw"]

            # Net power balance for this hour:
            #   surplus > 0 means renewable output exceeds scheduled demand
            #   deficit > 0 means demand exceeds renewable output
            surplus = max(0.0, gen - load_h)
            deficit = max(0.0, load_h - gen)

            if surplus > 0:
                # --- Charging branch (renewable surplus) ---
                # Charge rate is limited by both the inverter/charger max power and
                # the remaining headroom in the battery (space_avail).  The
                # efficiency factor converts AC input to stored DC energy:
                #   space_avail = (headroom_as_fraction_of_capacity) / eff_chg
                # so we account for charging losses when computing available space.
                charge_possible = min(surplus, max_chg)
                space_avail = (max_soc - soc) * cap / eff_chg
                actual_charge = min(charge_possible, space_avail)
                # Increase SOC: energy stored = actual_charge * eff_chg
                soc += (actual_charge * eff_chg) / cap
                total_battery_charge += actual_charge
                total_self_consumed += min(load_h, gen) + actual_charge
                total_exported += surplus - actual_charge
            elif deficit > 0:
                # --- Discharging branch (renewable deficit) ---
                # The battery can only supply energy above the minimum reserve (min_soc).
                # Discharging efficiency reduces the usable energy:
                #   energy_avail = (soc - min_soc) * cap * eff_dis
                # The SOC decrease uses the *gross* energy drawn from the battery
                # (actual_discharge / eff_dis) because eff_dis losses remain in
                # the battery as heat rather than reaching the load.
                total_self_consumed += gen
                discharge_possible = min(deficit, max_dis)
                energy_avail = (soc - min_soc) * cap * eff_dis
                actual_discharge = min(discharge_possible, energy_avail)
                soc -= (actual_discharge / eff_dis) / cap
                total_battery_discharge += actual_discharge
                rem_deficit = deficit - actual_discharge
                total_grid_energy += rem_deficit
            else:
                total_self_consumed += load_h

        # Cap self-consumption at total renewable generation to avoid physically
        # impossible values caused by floating-point accumulation across 24 hours.
        total_self_consumed = min(total_self_consumed, total_renewable)

        # Renewable self-consumption %:
        #   (energy consumed on-site from renewables) / (total renewable generated) × 100
        # A value of 100 % means every kWh of solar was used locally or stored;
        # a value < 100 % means some renewable energy was exported/curtailed.
        renewable_self_consumption_pct = (total_self_consumed / total_renewable * 100) if total_renewable > 0 else 0.0

        deadline_violations = sum(1 for s in schedule if s["status"] == "CONFLICT")
        total_flexible = sum(1 for s in schedule if s.get("priority") != "high" or s.get("duration_hours", 24) < 24)
        flexible_completed = sum(1 for s in schedule if s["status"] == "SCHEDULED" and (s.get("priority") != "high" or s.get("duration_hours", 24) < 24))
        flexible_completion_rate = (flexible_completed / total_flexible * 100) if total_flexible > 0 else 100.0

        # Heuristic disruption score (higher is worse)
        # 10 points per deadline violation, 5 points if load wasn't scheduled at earliest start
        user_disruption_score = deadline_violations * 10
        for s in schedule:
            if s["status"] == "SCHEDULED" and s.get("priority") != "high":
                # Assuming 'earliest_start' is roughly what user prefers
                # We can approximate by looking if priority is 'low' or 'medium'
                pass # Simple approximation: disruption is just deadline violations for now

        return {
            "renewable_self_consumption_pct": round(renewable_self_consumption_pct, 2),
            "renewable_export_kwh": round(total_exported, 2),
            "renewable_curtailment_kwh": round(total_exported, 2), # Synonym for this project
            "grid_energy_kwh": round(total_grid_energy, 2),
            "battery_charge_kwh": round(total_battery_charge, 2),
            "battery_discharge_kwh": round(total_battery_discharge, 2),
            "flexible_completion_rate": round(flexible_completion_rate, 2),
            "deadline_violations": deadline_violations,
            "comfort_violations": 0,
            "essential_interruptions": 0,
            "user_disruption_score": user_disruption_score,
            "total_renewable_kwh": round(total_renewable, 2),
            "self_consumed_kwh": round(total_self_consumed, 2)
        }
