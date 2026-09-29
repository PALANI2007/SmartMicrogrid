import pandas as pd
from typing import Tuple, List, Dict
from datetime import datetime


def validate_solar_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate and clean a solar generation DataFrame before further processing.

    The cleaning process applies the following transformations in order:

    1. **Schema check**: raises ``ValueError`` immediately if any of the six
       required columns (``timestamp``, ``solar_generation_kw``, ``temperature``,
       ``humidity``, ``cloud_cover``, ``wind_speed``) are absent, because
       downstream code cannot proceed without them.
    2. **Negative generation clipping**: solar panels cannot produce negative
       power; any negative values are sensor artefacts and are set to 0.
       A warning is appended when this occurs.
    3. **Timestamp parsing**: converts the ``timestamp`` column to
       ``pandas.Timestamp`` using ``pd.to_datetime``; raises ``ValueError`` on
       unrecognised formats.
    4. **Missing-value imputation**: forward-fills then backward-fills any NaN
       cells.  Forward-fill propagates the last valid reading forward (sensible
       for slowly-changing weather signals); backward-fill catches NaNs at the
       start of the series that forward-fill cannot reach.

    Parameters
    ----------
    df : pd.DataFrame
        Raw input DataFrame. Must contain the six required columns listed above.

    Returns
    -------
    tuple[pd.DataFrame, list[str]]
        A (cleaned_df, warnings) pair.  ``warnings`` is a list of human-readable
        messages describing any non-fatal data quality issues that were found and
        corrected.  An empty list means the data was clean.

    Raises
    ------
    ValueError
        If a required column is missing or if timestamp parsing fails.
    """
    warnings = []
    required_columns = [
        "timestamp", "solar_generation_kw", "temperature",
        "humidity", "cloud_cover", "wind_speed"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df = df.copy()

    if (df["solar_generation_kw"] < 0).any():
        warnings.append("Negative solar generation values found. Setting to 0.")
        df.loc[df["solar_generation_kw"] < 0, "solar_generation_kw"] = 0

    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    except Exception as e:
        raise ValueError(f"Invalid timestamp format: {e}")

    if df.isnull().any().any():
        warnings.append("Missing values found. Forward and backward filling applied.")
        df = df.ffill().bfill()

    return df, warnings


def validate_load(load_data: dict) -> Tuple[bool, str]:
    """
    Validate a load definition dict before it is stored or scheduled.

    Checks the following rules in order:

    1. ``power_kw`` must be strictly positive (zero-power loads are meaningless
       for scheduling and would corrupt power-balance calculations).
    2. ``duration_hours`` must be strictly positive (same reason).
    3. For **flexible** loads: if both ``earliest_start`` and ``latest_finish``
       are provided, ``earliest_start`` must be strictly before ``latest_finish``.
       Equal values leave zero scheduling headroom and are therefore rejected.
       Both times are expected in ``HH:MM`` format.
    4. ``priority`` must be one of ``"high"``, ``"medium"``, or ``"low"``; other
       values would cause the scheduler's priority map to silently default to 1
       (low), which is likely unintentional.

    Parameters
    ----------
    load_data : dict
        Load definition dict as stored in the database. Relevant keys:
        ``power_kw``, ``duration_hours``, ``load_type``, ``earliest_start``,
        ``latest_finish``, ``priority``.

    Returns
    -------
    tuple[bool, str]
        ``(True, "")`` if all checks pass, or ``(False, reason)`` with a
        human-readable explanation of the first failing check.
    """
    if load_data.get("power_kw", 0) <= 0:
        return False, "Power must be greater than 0"

    if load_data.get("duration_hours", 0) <= 0:
        return False, "Duration must be greater than 0"

    if load_data.get("load_type") == "flexible":
        es = load_data.get("earliest_start")
        lf = load_data.get("latest_finish")
        if es and lf:
            try:
                # Basic parsing assumes HH:00 format
                es_h = int(es.split(':')[0])
                lf_h = int(lf.split(':')[0])
                if es_h >= lf_h:
                    return False, "earliest_start must be before latest_finish"
            except Exception:
                return False, "Invalid time format for earliest_start/latest_finish"

    valid_priorities = ["high", "medium", "low"]
    if load_data.get("priority") not in valid_priorities:
        return False, f"Priority must be one of {valid_priorities}"

    return True, ""


def detect_forecast_error(predicted: float, actual: float, threshold_pct: float = 30.0) -> Dict:
    """
    Detect whether a forecast error is significant relative to a percentage threshold.

    The threshold logic follows a *relative error* definition:

        ``error_pct = |predicted - actual| / actual × 100``

    A special case applies when ``actual == 0``:
    - If ``predicted == 0`` as well, the error is 0 % (perfect night-time prediction).
    - If ``predicted > 0`` but ``actual == 0``, the relative error is infinite
      (the model predicted generation when none occurred — a complete miss).

    The ``threshold_pct`` default of 30 % is chosen to match the typical
    day-to-day variability of solar irradiance under partly cloudy conditions;
    errors below this level are considered operationally acceptable for
    scheduling purposes.

    Parameters
    ----------
    predicted : float
        Forecasted solar generation (kW) for a given hour.
    actual : float
        Measured solar generation (kW) for the same hour.
    threshold_pct : float, optional
        Relative error percentage above which an error is flagged as significant.
        Defaults to 30.0.

    Returns
    -------
    dict
        ``error_pct``     — computed percentage error (``float('inf')`` if
                            actual==0 and predicted!=0).
        ``is_significant`` — ``True`` if ``error_pct > threshold_pct``.
        ``direction``      — ``"overestimated"`` if predicted > actual,
                             ``"underestimated"`` otherwise.
    """
    if actual == 0:
        if predicted == 0:
            error_pct = 0.0
        else:
            error_pct = float('inf')
    else:
        error_pct = abs(predicted - actual) / actual * 100

    is_significant = error_pct > threshold_pct
    direction = "overestimated" if predicted > actual else "underestimated"

    return {
        "error_pct": error_pct,
        "is_significant": is_significant,
        "direction": direction
    }
