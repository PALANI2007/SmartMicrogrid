# Error Handling Documentation

## SmartMicrogrid — End-to-End Error Handling Reference

---

## 1. Overview

The SmartMicrogrid system handles errors at three distinct layers: the **backend (Python/FastAPI)**, the **ML/scheduler layer (Python)**, and the **frontend (React/TypeScript)**. Each layer has clearly defined responsibilities to ensure the application degrades gracefully rather than crashing.

---

## 2. Backend Error Handling

### 2.1 Global Exception Handler (`backend/app/main.py`)

A FastAPI application-level exception handler catches **any unhandled exception** from any endpoint and returns a consistent JSON error response:

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"message": str(exc)})
```

**Effect:** No endpoint can return a raw Python traceback to the client. All unexpected server-side errors produce:

```json
{
  "message": "<exception description string>"
}
```

### 2.2 Per-Endpoint HTTP Exceptions

Where business logic can detect an invalid condition before hitting the database or ML layer, endpoints raise `HTTPException` with a meaningful status code and detail:

| Endpoint | Condition | HTTP Status | Response |
|----------|-----------|-------------|----------|
| `POST /api/loads` | Load data fails `validate_load()` | 400 | `{"detail": "<validation message>"}` |
| `PUT /api/loads/{id}` | Load data fails `validate_load()` | 400 | `{"detail": "<validation message>"}` |
| `PUT /api/loads/{id}` | Load ID not found in database | 404 | `{"detail": "Load not found"}` |
| `DELETE /api/loads/{id}` | Load ID not found in database | 404 | `{"detail": "Load not found"}` |
| `GET /api/experiments/results/latest` | No experiment results in DB | 404 | `{"detail": "No experiment results found"}` |
| `GET /api/experiments/results/{run_id}` | `run_id` not found | 404 | `{"detail": "Experiment not found"}` |

### 2.3 Database Connection Error Handling

Database sessions are managed via FastAPI's `Depends(get_db)` dependency injection. The `get_db()` generator:

1. Opens a SQLAlchemy session.
2. Yields it to the endpoint function.
3. Closes the session in a `finally` block, ensuring the session is always closed even if an exception occurs.

If the SQLite file is missing or locked, SQLAlchemy raises an `OperationalError`, which is caught by the global exception handler and returned as `{"message": "..."}` with HTTP 500.

### 2.4 Model Loading Fallbacks

The `ForecastService` (`backend/app/services/forecast_service.py`) loads the pre-trained Random Forest model at import time. If the model file (`ml/models/forecast_model.joblib`) is missing:

- The service falls back to returning **zero-generation forecasts** for all 24 hours, ensuring the scheduler and dashboard do not crash.
- The `/api/forecast/metrics` endpoint still returns whatever is stored in `ml/models/metrics.json`; if that file is missing, it returns an empty dict `{}`.

### 2.5 Data Validation (`backend/app/utils/data_validation.py`)

Three validation functions are available:

#### `validate_solar_data(df: DataFrame) → (DataFrame, List[str])`

| Condition Checked | Action on Failure |
|------------------|-------------------|
| Missing required column | Raises `ValueError` (halts ingestion) |
| Negative `solar_generation_kw` values | Clamps to `0.0`; appends warning string |
| Invalid timestamp format | Raises `ValueError` |
| `NaN` / null values anywhere | Forward-fill then back-fill; appends warning |

#### `validate_load(load_data: dict) → (bool, str)`

| Condition Checked | Action on Failure |
|------------------|-------------------|
| `power_kw <= 0` | Returns `(False, "Power must be greater than 0")` |
| `duration_hours <= 0` | Returns `(False, "Duration must be greater than 0")` |
| Flexible load: `earliest_start >= latest_finish` | Returns `(False, "earliest_start must be before latest_finish")` |
| Flexible load: time format invalid | Returns `(False, "Invalid time format ...")` |
| `priority` not in `["high","medium","low"]` | Returns `(False, "Priority must be one of ...")` |

#### `detect_forecast_error(predicted, actual, threshold_pct=30.0) → dict`

Returns `{"error_pct": float, "is_significant": bool, "direction": str}`.
Used internally to flag large forecast deviations for the error-analysis endpoint.

---

## 3. Frontend Error Handling

### 3.1 React Error Boundary (`ErrorBoundary`)

A React `ErrorBoundary` component wraps the entire `App.tsx` component tree. If any child component throws a JavaScript error during rendering:

- The error boundary catches it, preventing a white-screen crash.
- A user-friendly fallback UI is displayed instead of the stack trace.
- The error is logged to the browser console for developer inspection.

```tsx
// In main.tsx / index.tsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### 3.2 `ErrorAlert` Component

Each page that makes API calls renders an `ErrorAlert` component conditionally:

```tsx
{error && <ErrorAlert message={error} />}
```

The `ErrorAlert` component displays a red alert box with the error message. It is only shown when the `error` state variable is non-null.

**Pages using `ErrorAlert`:** Dashboard, Forecast, Loads, Battery, Scheduler, Baseline Comparison, Experiments, Edge Cases, Validation.

### 3.3 `LoadingSpinner` Component

While API calls are in progress, pages display a `LoadingSpinner` instead of partial data:

```tsx
{loading && <LoadingSpinner />}
```

This prevents the user from interacting with stale or partially-loaded data.

### 3.4 API Call Try/Catch Pattern

Every API call in the frontend follows the same pattern:

```typescript
const fetchData = async () => {
  setLoading(true);
  setError(null);
  try {
    const response = await fetch('/api/endpoint');
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || errData.message || 'API error');
    }
    const data = await response.json();
    setData(data);
  } catch (err: any) {
    setError(err.message || 'An unexpected error occurred');
  } finally {
    setLoading(false);
  }
};
```

This pattern ensures:
- `loading` state is always reset in `finally`.
- Previous errors are cleared before each new attempt.
- Both HTTP error responses and network failures are caught.

---

## 4. Error Flow Diagram

```
User Action (button click / page load)
        │
        ▼
Frontend Component
   • setLoading(true)
   • setError(null)
        │
        ▼
API Call (fetch / axios)
        │
        ├─── Network Error ──────────────────────────────────────────────────┐
        │                                                                    │
        ▼                                                                    │
Backend FastAPI Handler                                                      │
   • validate inputs (validate_load / validate_solar_data)                  │
        │                                                                    │
        ├─── Validation Error (400 HTTPException) ───────────────────────┐  │
        │                                                                 │  │
        ▼                                                                 │  │
Database / ML Layer                                                       │  │
   • SQLAlchemy session                                                   │  │
   • ForecastEngine.predict()                                             │  │
        │                                                                 │  │
        ├─── Unexpected Exception ────────────────────────────────────┐  │  │
        │    (global_exception_handler → HTTP 500 JSON)               │  │  │
        │                                                             │  │  │
        ▼                                                             ▼  ▼  ▼
HTTP Response                                               Error Response
   200 OK + JSON data                                       {"message": str}
        │                                                   {"detail": str}
        ▼                                                        │
Frontend Response Handler                                        │
   • response.ok == true                                         │
   • setData(json)                              setError(message)◄┘
   • setLoading(false)                          setLoading(false)
        │                                            │
        ▼                                            ▼
Renders data / chart                         Renders <ErrorAlert>
```

---

## 5. API Error Response Format

All error responses from the backend use one of two formats:

**FastAPI `HTTPException` (client errors 4xx):**
```json
{
  "detail": "Human-readable error description"
}
```

**Global exception handler (server errors 5xx):**
```json
{
  "message": "Exception description string from str(exc)"
}
```

The frontend checks both `errData.detail` and `errData.message` when interpreting error responses.

---

## 6. Data Quality Error Handling

The `validate_solar_data` function is invoked during the ML training pipeline (data ingestion). Issues are handled non-destructively:

| Error Type | Handling Strategy |
|------------|-------------------|
| Missing required columns | Hard fail — `ValueError` raised, training aborted |
| Negative solar generation | Soft fix — values clamped to 0, warning emitted |
| Invalid timestamps | Hard fail — `ValueError` raised |
| NaN / missing values | Soft fix — forward-fill + back-fill applied, warning emitted |

Warnings are returned alongside the cleaned DataFrame, allowing the caller to log or display them without interrupting the pipeline.

---

## 7. Edge Case Graceful Fallback

The `EdgeCaseSimulator` (`scheduler/edge_cases.py`) is designed to always return a valid result dictionary rather than raising an exception:

- If a scenario has no schedulable loads, it returns `status='PASS'` with zero violations.
- CONFLICT loads are included in the schedule list with `status='CONFLICT'` and a non-empty `explanation` field.
- The API endpoint (`POST /api/edge-cases/run`) saves each scenario result to the database before returning, so partial failures are persisted.

---

## 8. Missing Model Fallback Behavior

| Condition | Fallback Behavior |
|-----------|------------------|
| `forecast_model.joblib` missing | `ForecastService` returns 24 zero-generation forecast entries |
| `features.json` missing | `ForecastEngine` cannot predict; `ForecastService` catches and returns empty list |
| `metrics.json` missing | `/api/forecast/metrics` and `/api/metrics` return `{}` |
| `BatteryConfig` row missing in DB | `edge_cases.py` and `battery.py` use hardcoded safe defaults (`capacity=10 kWh`, `SOC=50%`, etc.) |

---

## 9. What to Do When the Backend is Unavailable

If the backend server is not running or unreachable:

1. The frontend will show `<ErrorAlert message="Failed to fetch" />` on every page that makes an API call.
2. The `<LoadingSpinner />` will disappear after the request times out.
3. No data is lost — the backend database (`microgrid.db`) is persistent on disk.
4. Restart the backend with:
   ```powershell
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. Refresh the browser — all pages will reload their data automatically.
