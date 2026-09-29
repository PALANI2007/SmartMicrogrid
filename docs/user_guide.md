# User Guide

## SmartMicrogrid — Renewable-Aware Load Scheduling System

**Version:** 1.0.0 (Review 3)  
**Target Users:** Rural microgrid operators, facility managers, community grid administrators

---

## 1. Prerequisites and Starting the Application

### System Requirements

- Python 3.9 or later (backend)
- Node.js 18 or later (frontend)
- Modern browser (Chrome, Firefox, Edge, Safari)
- The project directory: `d:\Project\SmartMicrogrid`

### Starting the Backend

Open a PowerShell terminal and run:

```powershell
cd d:\Project\SmartMicrogrid\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Started server process [XXXX]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The backend API is now available at `http://localhost:8000`. You can view the auto-generated API docs at `http://localhost:8000/docs`.

### Starting the Frontend

**Option A — Using the PowerShell startup script:**
```powershell
cd d:\Project\SmartMicrogrid
.\start_frontend.ps1
```

**Option B — Using Node directly:**
```powershell
cd d:\Project\SmartMicrogrid\frontend
npm run dev
```

The frontend development server starts at `http://localhost:5173`.

Open this URL in your browser to use the application.

> **Note:** The backend must be running before the frontend can display live data. If the backend is unavailable, all pages will show an error alert and the app will not be functional until the backend is restarted.

---

## 2. Dashboard Walkthrough

The **Dashboard** is the first page you see after opening the application. It provides a real-time overview of your microgrid.

### Key Metrics Cards

| Card | Description |
|------|-------------|
| **Current Solar (kW)** | Live solar generation reading from the most recent forecast hour |
| **Predicted Solar (kW)** | ML model prediction for the current hour |
| **Total Load (kW)** | Sum of power across all active loads |
| **Essential Load (kW)** | Power consumed by essential loads only |
| **Flexible Load (kW)** | Power consumed by scheduled flexible loads |
| **Battery SOC** | Current State-of-Charge as a percentage |
| **Self-Consumption (%)** | How much solar is being used directly (higher = better) |
| **Renewable Export (kWh)** | Energy sent to grid (could have been used) |
| **Grid Dependency (%)** | Fraction of demand met by the grid (lower = better) |

### System Status Indicator

The **System Status** badge shows one of three states:

- 🟢 **Good** — All essential loads running, no conflicts, battery within safe range
- 🟡 **Warning** — Low battery SOC or minor scheduling conflicts detected
- 🔴 **Conflict** — Critical scheduling violation or essential load at risk

### Active Loads Table

The bottom of the dashboard lists all currently active loads with their scheduling status.

---

## 3. Solar Forecast Page

Navigate to **Forecast** in the sidebar.

### Understanding the Chart

The forecast chart shows 24 hourly bars (or a line chart) for today's date:

- **Blue line / bars** — Predicted solar generation (kW) from the Random Forest model
- **Shaded band** — Confidence interval (`lower_bound_kw` to `upper_bound_kw`). A narrow band means high confidence; a wide band indicates uncertainty.
- **Orange line** — Actual measured generation (if data is available for past hours)

### Reading the Confidence Interval

The confidence interval is dynamically estimated based on the Random Forest's individual tree predictions:
- At night (0 kW forced), the band narrows to zero.
- During cloud-prone hours (early morning, evening), the band widens.
- A `confidence_score` near `1.0` means the trees agree; near `0.5` means high spread.

### Error Distribution Section

The **Error Analysis** section below the chart shows:
- Hourly MAE (which hours are hardest to predict)
- Best-performing hour (lowest error)
- Worst-performing hour (highest error)
- Overall model MAE (0.0075 kW) vs baseline MAE (0.4268 kW)

### Training the Model

Click **Train Model** to retrain the Random Forest on all historical data in the database. This takes a few seconds and updates `ml/models/metrics.json`.

---

## 4. Load Management

Navigate to **Loads** in the sidebar.

### Understanding Load Types

| Type | Description | Scheduling |
|------|-------------|-----------|
| **Essential** | Must run 24/7 (medical equipment, refrigerators, basic lighting) | Always scheduled 00:00–24:00, never shifted |
| **Flexible** | Can be shifted to optimal solar windows (water pumps, EV chargers, irrigation) | Scheduled by the smart scheduler within your defined time window |

### Adding a New Load

1. Click **Add Load**.
2. Fill in the form:
   - **Name** — e.g., "Irrigation Pump"
   - **Type** — Essential or Flexible
   - **Power (kW)** — e.g., `1.5`
   - **Duration (hours)** — e.g., `2`
   - **Priority** — High, Medium, or Low
   - **Earliest Start** (flexible only) — e.g., `08:00`
   - **Latest Finish** (flexible only) — e.g., `18:00`
   - **Description** (optional)
3. Click **Save**.

> **Validation:** The system will reject the form if:
> - Power ≤ 0
> - Duration ≤ 0
> - `Earliest Start` ≥ `Latest Finish` for flexible loads
> - Priority is not High/Medium/Low

### Editing a Load

Click the **Edit** (pencil) icon next to any load to modify its parameters.

### Deleting a Load

Click the **Delete** (trash) icon next to any load. This permanently removes the load from the database.

### Deactivating a Load

Use the **Active** toggle to deactivate a load without deleting it. Inactive loads are excluded from scheduling.

---

## 5. Battery Page

Navigate to **Battery** in the sidebar.

### Understanding the Battery Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| **Capacity (kWh)** | Total energy the battery can store | 10.0 |
| **Current SOC** | Present State-of-Charge (0–100%) | ~50% |
| **Minimum SOC** | Safety floor — battery will not discharge below this | 20% |
| **Maximum SOC** | Upper charge limit — battery stops charging at this | 95% |
| **Max Charge Rate (kW)** | Maximum power the battery can absorb per hour | 3.0 |
| **Max Discharge Rate (kW)** | Maximum power the battery can deliver per hour | 3.0 |
| **Charging Efficiency** | Round-trip energy retained during charging | 95% |
| **Discharging Efficiency** | Energy delivered vs energy removed | 95% |

### SOC Simulation Chart

The **24-Hour SOC Simulation** chart shows how the battery SOC is predicted to evolve over the day given:
- The current solar forecast
- The total active load demand
- The current battery configuration

Key readings:
- **Total Charged (kWh)** — Total energy stored today
- **Total Discharged (kWh)** — Total energy drawn from battery today
- **Minimum SOC Reached** — The lowest SOC predicted during the day (should stay above `minimum_soc`)

### Updating Battery Parameters

Click **Update Battery** to save any changes to the configuration. The simulation chart refreshes automatically.

---

## 6. Smart Scheduler

Navigate to **Scheduler** in the sidebar.

### How to Run the Scheduler

1. Select a date (defaults to today).
2. Click **Run Smart Schedule**.
3. Wait 2–5 seconds for the scheduler to evaluate all loads.

### Reading the Results

The results table shows one row per load:

| Column | Description |
|--------|-------------|
| **Load Name** | The appliance name |
| **Type** | Essential or Flexible |
| **Priority** | High / Medium / Low |
| **Status** | SCHEDULED / CONFLICT / SKIPPED |
| **Start Time** | Scheduled start (`HH:MM`) |
| **End Time** | Scheduled end (`HH:MM`) |
| **Solar Available** | Average solar generation at the scheduled slot (kW) |
| **Battery Impact** | Net battery energy change from this slot (kWh) |

### Understanding Scheduling Explanations

Click any row to expand the **AI Explanation** for that load. Examples:

- *"Scheduled at 10:00 — this slot has the highest average renewable generation (4.8 kW), maximising self-consumption."*
- *"CONFLICT — No feasible time slot found within the window 08:00–12:00 for a 6-hour load. Window is too narrow."*
- *"Essential load — always active 00:00–24:00. No scheduling required."*

### Scheduler Metrics

After running, the metrics panel shows:
- **Renewable Self-Consumption (%)** — How much solar was used directly
- **Grid Energy (kWh)** — Energy imported from the grid
- **Renewable Export (kWh)** — Surplus solar sent to grid
- **Flexible Completion Rate (%)** — Fraction of flexible loads successfully scheduled
- **Deadline Violations** — Number of loads that could not be scheduled within their window

---

## 7. Baseline vs Smart Comparison Page

Navigate to **Comparison** in the sidebar.

This page runs both schedulers simultaneously and compares their performance side by side.

### How It Works

1. Click **Run Comparison**.
2. The system runs the **Baseline Scheduler** (naive first-come-first-served) and the **Smart Scheduler** simultaneously.
3. Results are shown in a comparison table.

### Reading the Comparison

| Metric | Baseline | Smart | Improvement |
|--------|----------|-------|-------------|
| Self-Consumption (%) | ~41% | ~78% | +37% |
| Grid Energy (kWh) | ~4.3 | ~1.2 | -3.1 |
| Renewable Export (kWh) | ~16.6 | ~6.3 | -10.3 |

> A positive improvement for self-consumption (higher = better) and a negative improvement for grid energy and export (lower = better) indicate the smart scheduler is working correctly.

---

## 8. Experiments Page

Navigate to **Experiments** in the sidebar.

### Running an Experiment

1. Enter an **Experiment Name** (optional, defaults to date + time).
2. Select a **Date** to simulate.
3. Click **Run Experiment**.

### Reading Experiment Results

Each experiment shows:
- Side-by-side baseline and smart scheduler schedules
- Improvement metrics for each KPI
- A historical list of past experiments

This page is useful for comparing different load configurations or dates to understand when the smart scheduler provides the greatest benefit.

---

## 9. Edge Case Analysis Page

Navigate to **Edge Cases** in the sidebar (or check the **Alerts** section).

### What Are Edge Cases?

Edge cases test the scheduler's robustness under abnormal conditions:

| Scenario | Description |
|----------|-------------|
| **Monsoon / Cloud Cover** | Near-zero solar generation for the full day |
| **Low Battery** | Battery starts at near-minimum SOC (22%) |
| **Essential Load Surge** | An emergency essential load is added during peak hours |
| **Deadline Conflict** | A flexible load has an infeasible time window |

### How to Run Edge Cases

1. Select a specific scenario or choose **Run All Scenarios**.
2. Click **Run**.
3. Results appear in a table with status (PASS/FAIL), violations count, and explanation.

### Interpreting Results

- **PASS** — The scheduler handled the scenario gracefully: essential loads were protected, battery bounds were respected, and conflicts were explicitly reported.
- **FAIL** — The scenario revealed a case where the scheduler produced unacceptable output (none currently in the implementation).
- **Violations** — Shows counts for essential load interruptions, battery bound violations, and deadline conflicts.

---

## 10. Settings — Language Switching

Navigate to **Settings** (gear icon) in the navigation bar.

### Switching Between English and Tamil

Click the language toggle button:
- **English** — Full English UI
- **தமிழ்** — Full Tamil UI (Unicode Tamil script)

The language switch is instant and persistent within the browser session. All page titles, labels, button text, and status messages are translated.

> Tamil translations are stored in `frontend/src/i18n/ta.ts` as Unicode Tamil script strings. The translation covers all 10 UI sections: dashboard, forecast, loads, battery, scheduler, comparison, experiments, edge cases, settings, and help.

---

## 11. Help & Guide Page

Navigate to **Help** in the sidebar.

The Help page provides:
- A summary of all features
- Definitions of key terms (SOC, self-consumption, curtailment, etc.)
- Quick-start instructions
- Links to the scheduler formulation documentation

---

## 12. What to Do When the Backend is Unavailable

If the backend is not running, you will see an error like:
> **"Failed to fetch"** or **"Network error"**

**Steps to restore service:**

1. Open a new PowerShell terminal.
2. Navigate to the backend folder:
   ```powershell
   cd d:\Project\SmartMicrogrid\backend
   ```
3. Start the backend:
   ```powershell
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
4. Refresh the browser page. All data will reload automatically.

**No data is lost** — the SQLite database (`microgrid.db`) is stored on disk and persists between restarts.

---

## 13. Interpreting Scheduling Recommendations

### When to Trust the Smart Scheduler

The smart scheduler is most reliable when:
- You have ≥ 3 hours of historical solar data for the forecast date's season
- All load time windows are at least `duration_hours + 1` wide
- The battery is above 40% SOC at the start of the day

### When to Override Manually

Consider manual adjustments when:
- The scheduler shows CONFLICT for a high-priority load — check if the time window can be widened.
- The battery SOC is forecast to drop below 25% during essential load hours.
- Grid events (planned outages) are not captured in the current dataset.

### Understanding Self-Consumption vs Export

- **High self-consumption (>70%)**: The scheduler successfully aligned flexible loads with solar peaks. Minimal grid import.
- **High export**: More solar is being generated than loads can consume. Consider adding more flexible loads or battery capacity.
- **High grid energy**: Solar is insufficient to cover demand. This is expected during monsoon season or cloudy days.
