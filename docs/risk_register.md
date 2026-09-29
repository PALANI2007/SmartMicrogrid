# Risk Register

## SmartMicrogrid — Comprehensive Risk Register

**Version:** Review 3 Final  
**Project:** Renewable-Aware Load Scheduler for Rural Microgrid (Tamil Nadu)

---

## Risk Rating Scale

| Rating | Likelihood | Impact |
|--------|-----------|--------|
| H | High — likely to occur in normal operation | High — significant degradation of service or data loss |
| M | Medium — possible under certain conditions | Medium — reduced performance, user confusion |
| L | Low — unlikely under normal conditions | Low — minor inconvenience, easy to recover |

---

## Risk Register Table

| Risk ID | Risk | Cause | Impact | Likelihood | Mitigation | Detection | Residual Risk |
|---------|------|-------|--------|------------|------------|-----------|---------------|
| **R01** | **Forecast error** — RF model inaccuracy due to weather variability | Unexpected cloud cover, monsoon onset, or dust storms not represented in training data (Jan–Jun 2024 synthetic set) | Scheduler assigns flexible loads to low-solar windows, increasing grid import | M | Confidence intervals displayed on forecast chart warn operator; scheduler uses lower-bound generation in conservative mode; retrain with `POST /api/forecast/train` after each season | Confidence score drops below 0.70; large shaded band on forecast chart | M |
| **R02** | **Renewable intermittency** — Unpredictable cloud cover causing intra-hour solar drops | Scattered cumulus clouds not captured by hourly weather features | Flexible loads running during "cloud shadow" hours draw from battery or grid unexpectedly | H | Edge case `monsoon_cloud_cover` validated (PASS); battery discharge constraint enforced; essential loads always protected | `monsoon_cloud_cover` edge case status changes to FAIL | M |
| **R03** | **Sensor/data quality** — Missing or corrupted sensor readings during data ingestion | Communication failure, sensor malfunction, or corrupt CSV upload | Training data poisoning; model learns incorrect feature relationships | M | `validate_solar_data()` auto-detects negatives, NaNs, and missing columns; warnings surfaced to operator; invalid rows clamped/filled | Validation warnings appear in ingestion log | L |
| **R04** | **Battery degradation** — Capacity reduction over time due to charge cycles | Natural Li-ion / lead-acid cell aging; deep discharge events | Actual usable capacity less than `capacity_kwh` in database; SOC simulations become inaccurate | L | `minimum_soc = 0.20` and `maximum_soc = 0.95` enforced in software to limit depth-of-discharge; `PUT /api/battery` allows operator to update `capacity_kwh` as degradation is measured | Battery consistently reaching `minimum_soc` earlier than predicted | M |
| **R05** | **Communication/network failure** — API unavailable (backend server crash or network partition) | OS crash, power loss, process kill, or port conflict | Frontend cannot display data; operators cannot run scheduler or view status | M | React `ErrorBoundary` prevents white-screen crash; `ErrorAlert` informs user; SQLite data persists on disk; backend restarts with single command | Frontend shows "Failed to fetch" error on all pages | L (data preserved) |
| **R06** | **Unexpected essential load surge** — Emergency equipment addition (e.g., ICU ventilator added mid-day) | Unplanned equipment deployment at facility | Essential load demand exceeds solar + battery capacity; grid draw spikes | M | `essential_load_surge` edge case validated (PASS); essential loads always scheduled 00:00–24:00; scheduler re-runs on demand; power capacity constraint (15 kW) prevents overload | New essential load added to database triggers scheduler re-run alert | M |
| **R07** | **Deadline conflicts** — Infeasible scheduling windows (flexible load duration > window size) | Operator enters `earliest_start` too close to `latest_finish`; or load duration is larger than the window | Flexible load receives `CONFLICT` status; unscheduled demand may fall on grid | H | `validate_load()` enforces `earliest_start < latest_finish`; `deadline_conflict` edge case validated (PASS); CONFLICT status shown with non-empty explanation; operator prompted to widen window | CONFLICT status in scheduler results | L (graceful) |
| **R08** | **Model drift** — Changing seasonal patterns not reflected in training data | Dataset covers Jan–Jun 2024 only; patterns for Jul–Dec differ significantly | Forecast accuracy degrades for Q3/Q4; scheduler makes sub-optimal slot selections | M | `POST /api/forecast/train` retrains on all available data; R² monitored via `/api/forecast/metrics`; retrain quarterly or when R² drops below 0.90 | Model MAE rises above 0.05 kW on test set | M |
| **R09** | **API/backend failure** — Server process crash or unhandled exception | Bug in service layer, out-of-memory condition, or database lock | All API endpoints return 500 errors; frontend unusable | L | Global `exception_handler` in `main.py` catches all unhandled exceptions and returns JSON 500 response (no raw traceback); 31-test suite catches regressions before deployment | HTTP 500 responses from `/api/health` | L |
| **R10** | **Database corruption** — SQLite file corruption | Power loss during write, disk full, or concurrent write from multiple processes | Loss of scheduled data, experiment results, or validation responses | L | SQLite WAL mode provides crash safety; data is re-creatable (loads can be re-entered; solar_data loaded from CSV; model retrained); regular file backup recommended | `sqlite3` integrity check fails on startup | M |
| **R11** | **User misunderstanding** — Operator misinterprets scheduling recommendations | XAI explanation text is too technical; operator unfamiliar with kWh/kW distinction | Wrong manual overrides; essential loads inadvertently deactivated; battery drained | M | Plain-language explanations in both English and Tamil; status colour coding (green/amber/red); user guide documents key metrics; validation questionnaire Q2 monitors explanation clarity | Q2 average falls below 3.5 in validation | M |
| **R12** | **Incorrect scheduling constraints** — Wrong load configuration (e.g., zero duration, negative power) | Data entry error by operator | Scheduler crashes or produces invalid schedule; downstream experiment results corrupted | H | `validate_load()` enforces `power_kw > 0`, `duration_hours > 0`, valid time format; HTTP 400 returned with descriptive message; UI form shows inline error | 400 response from `POST /api/loads` | L |

---

## Risk Summary

| Level | Count | Risk IDs |
|-------|-------|---------|
| High Likelihood | 2 | R02, R07 |
| Medium Likelihood | 7 | R01, R03, R05, R06, R08, R11, R12 |
| Low Likelihood | 3 | R04, R09, R10 |

### Highest Priority Risks (H Impact + H/M Likelihood)

1. **R02** (Renewable Intermittency) — Mitigated by edge case testing and battery constraints.
2. **R07** (Deadline Conflicts) — Mitigated by input validation and graceful CONFLICT handling.
3. **R01** (Forecast Error) — Mitigated by confidence intervals and seasonal retraining.

---

## Risk Monitoring Schedule

| Frequency | Action |
|-----------|--------|
| Daily | Check system status on dashboard; look for CONFLICT or WARNING indicators |
| Weekly | Review `GET /api/forecast/metrics` for R² degradation |
| Monthly | Run all edge cases (`POST /api/edge-cases/run` with `scenario_id: "all"`) |
| Quarterly | Retrain model with new data (`POST /api/forecast/train`); update `capacity_kwh` if battery degradation observed |
| After incidents | Add new load or weather pattern as test case; check `validate_solar_data()` warnings |
