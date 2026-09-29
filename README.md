# Renewable-Aware Load Scheduler for Rural Microgrid

![Project Status](https://img.shields.io/badge/Status-Review%203%20Final%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-teal)
![React](https://img.shields.io/badge/React-18.3-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-blue)
![Vite](https://img.shields.io/badge/Vite-4.5.14-purple)
![License](https://img.shields.io/badge/License-MIT-green)

An intelligent, machine-learning-driven load scheduling and energy management system designed to optimize renewable self-consumption, minimize grid dependency, and protect critical essential loads in rural Indian microgrids.

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Key Features](#3-key-features)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Project Directory Structure](#6-project-directory-structure)
7. [Dataset Overview](#7-dataset-overview)
8. [Machine Learning Forecast Pipeline](#8-machine-learning-forecast-pipeline)
9. [Mathematical Scheduler Formulation](#9-mathematical-scheduler-formulation)
10. [Key Performance Metrics](#10-key-performance-metrics)
11. [Installation & Setup](#11-installation--setup)
12. [Backend Setup & Running](#12-backend-setup--running)
13. [Frontend Setup & Running](#13-frontend-setup--running)
14. [Database Initialization](#14-database-initialization)
15. [Training the ML Model](#15-training-the-ml-model)
16. [Running the Full Application](#16-running-the-full-application)
17. [Running Tests](#17-running-tests)
18. [Running Edge-Case Simulations](#18-running-edge-case-simulations)
19. [Running Baseline vs Smart Experiments](#19-running-baseline-vs-smart-experiments)
20. [REST API Documentation Summary](#20-rest-api-documentation-summary)
21. [Database Schema Summary](#21-database-schema-summary)
22. [Error Handling & Error Boundaries](#22-error-handling--error-boundaries)
23. [Accessibility Features](#23-accessibility-features)
24. [Multilingual Support (English & Tamil)](#24-multilingual-support-english--tamil)
25. [Stakeholder Validation Framework](#25-stakeholder-validation-framework)
26. [Risk Register & Mitigation](#26-risk-register--mitigation)
27. [Experimental Results & Comparison](#27-experimental-results--comparison)
28. [Reproducibility Guide](#28-reproducibility-guide)
29. [Known Limitations](#29-known-limitations)
30. [Future Scope](#30-future-scope)
31. [Documentation Index & License](#31-documentation-index--license)

---

## 1. Problem Statement

Rural microgrids in southern India (such as Tamil Nadu) rely heavily on solar generation paired with battery storage systems. However, solar intermittency caused by monsoon weather patterns and limited battery capacity often results in:
- High reliance on expensive, unstable utility grid power.
- Solar energy curtailment during midday generation peaks.
- Unexpected battery depletion disrupting essential loads (e.g., medical refrigeration, drinking water pumps).
- Inefficient fixed-schedule appliance operation.

## 2. Solution Overview

This project implements an end-to-end **Renewable-Aware Load Scheduler** that:
1. Predicts hourly solar generation using a **Random Forest Regressor** trained on 6 months of historical weather and generation data.
2. Calculates empirical prediction intervals ($\pm 1.645 \times \sigma$) to quantify forecast uncertainty.
3. Optimizes flexible load execution windows using a **weighted-scoring constraint satisfaction algorithm**.
4. Guarantees non-disruption of high-priority essential loads.
5. Provides an intuitive dark-themed **React + TypeScript frontend** with English and Tamil UTF-8 localization.

---

## 3. Key Features

- **ML Solar Forecasting:** 24-hour horizon predictions with Random Forest (MAE 0.0075 kW, $R^2$ 0.9979).
- **Smart Renewable Scheduler:** Priority-aware load shifting aligning flexible demand with solar generation peaks.
- **Essential Load Protection:** Guaranteed zero interruption for critical loads (medical equipment, refrigeration).
- **Battery Optimization:** State of Charge (SOC) tracking protecting battery health within 20%–95% limits.
- **Edge-Case Stress Testing:** 4 automated scenario simulators (Monsoon Cloud Cover, Low Battery, Essential Surge, Deadline Conflict).
- **Interactive Dark Dashboard:** 11 visual management pages with real-time charts (Recharts).
- **Full Tamil Localization:** Native Tamil text support across all pages (`frontend/src/i18n/ta.ts`).
- **React Error Boundaries:** Component-level error isolation preventing application crashes.
- **WCAG Accessibility:** Keyboard navigation skip links (`#main-content`) and ARIA labels.

---

## 4. System Architecture

```
                               ┌────────────────────────────────┐
                               │     React 18 + TS Frontend     │
                               │  (Vite / Tailwind / Recharts)  │
                               └──────────────┬─────────────────┘
                                              │ REST API (JSON)
                                              ▼
                               ┌────────────────────────────────┐
                               │      FastAPI Backend Engine    │
                               │  (Python 3.11 / Pydantic v2)   │
                               └──────┬──────────────────┬──────┘
                                      │                  │
                ┌─────────────────────┴──┐            ┌──┴──────────────────────┐
                ▼                        ▼            ▼                         ▼
      ┌──────────────────┐    ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐
      │ ML Forecast Model│    │ Smart Scheduler  │  │ Battery Simulator│  │SQLite DB  │
      │(Random Forest Engine)│  │(Priority-Weighted│  │ (SOC & Efficiency│  │(microgrid │
      └──────────────────┘    │   Constraints)   │  │   Modeler)       │  │   .db)    │
                              └──────────────────┘  └──────────────────┘  └───────────┘
```

---

## 5. Technology Stack

| Layer | Technology / Library | Version | Purpose |
|-------|----------------------|---------|---------|
| **Backend Framework** | FastAPI | 0.111.0 | Asynchronous RESTful API framework |
| **Server** | Uvicorn | 0.29.0 | ASGI web server |
| **Database ORM** | SQLAlchemy | 2.0.30 | SQLite object-relational mapping |
| **Data Validation** | Pydantic | 2.7.1 | Data parsing and schema validation |
| **ML Engine** | Scikit-Learn | 1.4.2 | Random Forest regression modeling |
| **Data Processing** | Pandas / NumPy | 2.2.2 / 1.26.4 | Dataset transformation and metrics |
| **Frontend UI** | React / TypeScript | 18.3 / 5.2 | Component-based user interface |
| **Build Tool** | Vite | 4.5.14 | High-performance frontend bundler |
| **Styling** | Tailwind CSS | 3.4.3 | Utility-first dark dashboard design |
| **Data Visualization**| Recharts | 2.12.7 | Interactive charts and analytics |
| **Localization** | i18next / react-i18next | 23.11.3 | English & Tamil internationalization |
| **Testing** | Pytest / pytest-asyncio | 8.2.0 | Automated backend unit & API tests |

---

## 6. Project Directory Structure

```
SmartMicrogrid/
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # API Route Controllers (13 Routers)
│   │   ├── services/         # Business Logic & Analytics Services
│   │   ├── utils/            # Helper Utilities & Validation Rules
│   │   ├── config.py         # App Environment Configuration
│   │   ├── database.py       # SQLAlchemy Session Initialization
│   │   ├── main.py           # Application Entry Point & Exception Handlers
│   │   ├── models.py         # Database ORM Schema (8 Tables)
│   │   └── schemas.py        # Pydantic Schemas
│   ├── seed_database.py      # Database Seeder (Populates 6 Months Data)
│   └── requirements.txt      # Python Dependencies
├── frontend/                 # React + TypeScript Vite Frontend
│   ├── src/
│   │   ├── components/       # Reusable UI Components & ErrorBoundary
│   │   ├── i18n/             # i18n Translations (en.ts, ta.ts)
│   │   ├── pages/            # 11 Page Components
│   │   ├── services/api.ts   # Axios API Client & Endpoints
│   │   ├── types/index.ts    # TypeScript Type Definitions
│   │   ├── App.tsx           # Application Router
│   │   └── main.tsx          # React Root Mount
│   └── package.json          # Node Dependencies & Scripts
├── ml/                       # Machine Learning Pipeline
│   ├── models/               # Saved Artifacts (.joblib, features.json, metrics.json)
│   ├── forecast.py           # Inference Engine
│   ├── train_forecast.py     # Training Script
│   └── evaluate.py           # Error Metrics Evaluator
├── scheduler/                # Optimization Engine
│   ├── baseline_scheduler.py # Naive Earliest-Start Scheduler
│   ├── constraints.py        # Microgrid Hard & Soft Constraints
│   ├── edge_cases.py         # 4 Edge-Case Stress Simulators
│   ├── metrics.py            # Hourly Simulation Metrics Calculator
│   └── scheduler_engine.py   # Renewable-Aware Smart Scheduler
├── data/                     # Dataset Files
│   └── processed/dataset.csv # 4,368 Hourly Data Samples (Jan-Jun 2024)
├── docs/                     # Comprehensive System Documentation
│   ├── api.md                # REST API Reference
│   ├── database_schema.md    # ER Diagram & Table Specs
│   ├── error_handling.md     # Error Boundaries & Fallback Flow
│   ├── ml_evaluation.md      # Forecast Performance Evaluation
│   ├── review_3_final_report.md # Final Milestone Completion Report
│   ├── risk_register.md      # System Risk Matrix & Mitigations
│   ├── scheduler_formulation.md # Mathematical Optimization Model
│   ├── testing.md            # Automated Testing Documentation
│   ├── user_guide.md         # Step-by-Step Operator Guide
│   └── validation.md         # Stakeholder Validation Framework
└── README.md                 # Master Project Documentation
```

---

## 7. Dataset Overview

- **Dataset Path:** `data/processed/dataset.csv`
- **Sample Count:** 4,368 hourly records (24 hours/day $\times$ 182 days = 6 months).
- **Date Range:** January 1, 2024 to June 30, 2024.
- **Columns:** `timestamp`, `solar_generation_kw`, `temperature_c`, `humidity_pct`, `cloud_cover_pct`, `wind_speed_ms`, `irradiance_wm2`, `load_demand_kw`, `battery_soc_pct`.
- **Data Quality:** Chronologically sorted, 0 missing values, 0 negative solar generation values, 0 duplicate timestamps.

---

## 8. Machine Learning Forecast Pipeline

The forecast engine predicts 24-hour solar generation horizons:
1. **Feature Engineering:** Extracts `hour`, `day_of_week`, `month`, `is_daytime`, solar lags (`1h`, `2h`, `24h`), and rolling averages (`3h`, `6h`).
2. **Split Strategy:** Strict **chronological 80/20 train/test split** (3,475 train samples, 869 test samples) to prevent data leakage.
3. **Model:** `RandomForestRegressor(n_estimators=200, random_state=42)`.
4. **Uncertainty Quantification:** Computes standard deviation across individual tree predictions to establish empirical 90% confidence bounds ($\pm 1.645 \times \sigma$).

### Model Performance

| Metric | Random Forest Model | Naive 24h Baseline |
|--------|----------------------|--------------------|
| **MAE** | **0.0075 kW** | 0.4268 kW |
| **RMSE** | **0.0646 kW** | 0.7585 kW |
| **$R^2$ Score** | **0.9979** | 0.7052 |

---

## 9. Mathematical Scheduler Formulation

The smart scheduler maximizes solar self-consumption while satisfying microgrid constraints:

$$\max \sum_{i \in \text{Loads}} \left[ 2.0 \cdot G_{\text{surplus}}(t) + 1.0 \cdot w_{\text{priority}}(i) - 1.5 \cdot |\Delta \text{SOC}| + 0.5 \cdot t_{\text{margin}} \right]$$

### Constraints Enforced
1. **Essential Load Protection:** $P_{\text{essential}}(t)$ is scheduled unconditionally (cannot be shifted or shedding).
2. **Flexible Load Windows:** $t_{\text{start}} \ge \text{earliest\_start}$ and $t_{\text{start}} + \text{duration} \le \text{latest\_finish}$.
3. **Battery Storage Limits:** $0.20 \le SOC(t) \le 0.95$.
4. **Power Balance:** $G(t) + P_{\text{discharge}}(t) = P_{\text{load}}(t) + P_{\text{charge}}(t) + P_{\text{grid}}(t) + P_{\text{curtail}}(t)$.

---

## 10. Key Performance Metrics

- **Renewable Self-Consumption:** Increased from **64.2% (Baseline)** to **97.4% (Smart Scheduler)**.
- **Grid Energy Dependence:** Reduced from **18.4 kWh/day** to **2.1 kWh/day** (88.6% reduction).
- **Essential Load Violations:** **0%** (100% essential load protection).

---

## 11. Installation & Setup

### Prerequisites
- **Python:** 3.11+
- **Node.js:** v18+ or v20+
- **Git:** Installed

```bash
git clone https://github.com/PALANI2007/SmartMicrogrid.git
cd SmartMicrogrid
```

---

## 12. Backend Setup & Running

```bash
# Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r backend/requirements.txt

# Set PYTHONPATH
$env:PYTHONPATH="d:\Project\SmartMicrogrid"

# Initialize database & seed initial data
python backend/seed_database.py

# Start FastAPI backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 13. Frontend Setup & Running

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev

# Or build for production
npm run build
```

---

## 14. Database Initialization

Database initialization occurs automatically when starting the backend server via `init_db()`. To manually seed the SQLite database (`backend/microgrid.db`):

```bash
$env:PYTHONPATH="d:\Project\SmartMicrogrid"
python backend/seed_database.py
```

---

## 15. Training the ML Model

To retrain the Random Forest model on the dataset:

```bash
$env:PYTHONPATH="d:\Project\SmartMicrogrid"
python ml/train_forecast.py
```

Artifacts are saved automatically to `ml/models/forecast_model.joblib`, `features.json`, and `metrics.json`.

---

## 16. Running the Full Application

1. **Backend Server:** Runs at `http://localhost:8000` (API documentation at `http://localhost:8000/docs`).
2. **Frontend UI:** Access at `http://localhost:5173`.

---

## 17. Running Tests

Run the full automated test suite (31 tests across backend APIs, ML engine, battery models, metrics, and edge cases):

```bash
$env:PYTHONPATH="d:\Project\SmartMicrogrid"
pytest -v
```

**Output:** `31 passed in 7.35s`.

---

## 18. Running Edge-Case Simulations

To test the 4 extreme microgrid stress scenarios:

```bash
$env:PYTHONPATH="d:\Project\SmartMicrogrid"
python -c "
from scheduler.edge_cases import EdgeCaseSimulator
sim = EdgeCaseSimulator()
for scenario in ['monsoon_cloud_cover', 'low_battery', 'essential_load_surge', 'deadline_conflict']:
    res = sim.run_scenario(scenario, [], {})
    print(f'{scenario}: {res[\"status\"]}')
"
```

Or trigger via API: `POST http://localhost:8000/api/edge-cases/run` with body `{"scenario_id": "all"}`.

---

## 19. Running Baseline vs Smart Experiments

To compare the baseline scheduler against the smart scheduler:

```bash
$env:PYTHONPATH="d:\Project\SmartMicrogrid"
python -c "
from scheduler.experiments import ExperimentRunner
runner = ExperimentRunner()
res = runner.run_experiment('2024-06-15', 'CLI_Test')
print('Smart Self-Consumption:', res['optimized']['renewable_self_consumption_pct'])
"
```

---

## 20. REST API Documentation Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Backend status & version check |
| `GET` | `/api/dashboard` | Dashboard metrics, active loads, hourly telemetry |
| `GET` | `/api/forecast` | 24-hour solar generation forecast & uncertainty bounds |
| `GET` | `/api/forecast/metrics` | Model MAE, RMSE, $R^2$ vs baseline |
| `GET` | `/api/forecast/errors` | Empirical error distribution & percentiles |
| `POST` | `/api/forecast/train` | Retrain Random Forest model on latest data |
| `GET` | `/api/loads` | Retrieve all microgrid loads |
| `POST` | `/api/loads` | Create new microgrid load |
| `GET` | `/api/battery` | Battery SOC & configuration settings |
| `PUT` | `/api/battery` | Update battery parameters |
| `POST` | `/api/scheduler/run` | Run smart renewable-aware scheduler |
| `POST` | `/api/baseline/run` | Run naive earliest-start baseline scheduler |
| `POST` | `/api/experiments/run` | Run baseline vs smart comparison experiment |
| `GET` | `/api/edge-cases` | Retrieve edge-case scenario historical runs |
| `POST` | `/api/edge-cases/run` | Trigger edge-case simulation execution |

*Full API specification available in [docs/api.md](docs/api.md).*

---

## 21. Database Schema Summary

The database uses SQLite (`microgrid.db`) managed via SQLAlchemy ORM (8 tables):
- `solar_data`: Historical solar generation & weather parameters.
- `loads`: Microgrid loads (essential vs flexible, power, duration, windows, priority).
- `battery_config`: Battery capacity, SOC limits, and charge/discharge efficiencies.
- `forecasts`: Model predictions, confidence bounds, and actual generation.
- `schedules`: Scheduled start/end times, renewable allocation, and status (`SCHEDULED`/`CONFLICT`).
- `experiment_results`: Baseline vs smart metric comparisons.
- `edge_case_results`: Stress scenario simulation outcomes.
- `validation_responses`: Stakeholder feedback questionnaire scores (Q1–Q6).

*Full schema details available in [docs/database_schema.md](docs/database_schema.md).*

---

## 22. Error Handling & Error Boundaries

- **Frontend:** Wrapped with `ErrorBoundary.tsx` class component to catch rendering errors gracefully without crashing the application.
- **Backend:** Global FastAPI exception handler catches unhandled exceptions and returns standardized `500` JSON responses.
- **Data Validation:** `validate_solar_data()` cleans bad sensor input; `validate_load()` verifies constraint feasibility.

*Full details available in [docs/error_handling.md](docs/error_handling.md).*

---

## 23. Accessibility Features

- **Keyboard Navigation:** `#main-content` skip-to-content link for screen readers and keyboard-only users.
- **ARIA Labels:** Explicit `aria-label="Main navigation"` on sidebar navigation.
- **Contrast & Styling:** High-contrast dark theme (slate-950 background) with clear status badges.

---

## 24. Multilingual Support (English & Tamil)

The frontend features dynamic language switching between English (`en.ts`) and native Tamil (`ta.ts`):
- 2,001 UTF-8 Tamil characters supporting all dashboard views, explanations, forms, and alerts.
- Toggle available directly in top navigation header.

---

## 25. Stakeholder Validation Framework

- **6-Question Survey:** Measures understandability (Q1), explanation clarity (Q2), disruption (Q3), visual readability (Q4), Tamil language usefulness (Q5), and confidence intervals (Q6).
- **Academic Prototype Note:** Seeded with 5 demonstration responses (Average Score: **4.27 / 5.0**).
- *Full specification available in [docs/validation.md](docs/validation.md).*

---

## 26. Risk Register & Mitigation

12 system risks analyzed across technical, hardware, data quality, and operational domains:
- **Forecast Inaccuracy (R01):** Mitigated by uncertainty bounds & error distribution analytics.
- **Extended Monsoons (R02):** Mitigated by grid fallback & monsoon edge-case testing.
- **Essential Load Surge (R06):** Mitigated by strict priority scheduling hard constraints.

*Full risk matrix available in [docs/risk_register.md](docs/risk_register.md).*

---

## 27. Experimental Results & Comparison

| Metric | Baseline Scheduler | Smart Scheduler | Net Improvement |
|--------|-------------------|-----------------|-----------------|
| **Renewable Self-Consumption** | 64.2% | **97.4%** | **+33.2%** |
| **Grid Energy Import** | 18.4 kWh/day | **2.1 kWh/day** | **-88.6%** |
| **Essential Interruptions** | 0 | **0** | **0 (Protected)** |
| **Deadline Violations** | 1 | **0** | **-100%** |

---

## 28. Reproducibility Guide

To reproduce all model evaluation metrics, scheduler benchmarks, and test results:
1. Initialize clean database: `python backend/seed_database.py`.
2. Execute model training: `python ml/train_forecast.py`.
3. Run test suite: `pytest -v`.
4. Trigger API experiment: `POST http://localhost:8000/api/experiments/run`.

---

## 29. Known Limitations

1. **Synthetic Dataset:** Current evaluation uses synthetic solar generation data derived mathematically from irradiance and temperature. Real hardware sensor noise will reduce model $R^2$.
2. **Greedy Heuristic Scheduler:** The scheduler uses a priority-weighted greedy heuristic rather than a global Mixed-Integer Linear Programming (MILP) solver. While fast (<50ms), it does not guarantee global mathematical optimality.
3. **Academic Stakeholder Data:** Validation survey responses are demonstration data created during database seeding.

---

## 30. Future Scope

- **MILP Optimization:** Integration of PuLP/SciPy MILP solver for exact global optimization.
- **Hardware Integration:** Modbus/MQTT drivers for real-time solar inverter telemetry.
- **Mobile Application:** React Native mobile interface for rural microgrid operators.

---

## 31. Documentation Index & License

### Documentation Index
- 📘 [Mathematical Scheduler Formulation](docs/scheduler_formulation.md)
- 📊 [ML Model Evaluation](docs/ml_evaluation.md)
- 📈 [Forecast Error Analysis](docs/error_analysis.md)
- 🧪 [Automated Testing Strategy](docs/testing.md)
- 🛡️ [Error Handling Architecture](docs/error_handling.md)
- 🔌 [REST API Reference](docs/api.md)
- 🗄️ [Database Schema & ER Diagrams](docs/database_schema.md)
- 📖 [User & Operator Guide](docs/user_guide.md)
- 📋 [Stakeholder Validation Framework](docs/validation.md)
- ⚠️ [Risk Register & Matrix](docs/risk_register.md)
- 📑 [Review 3 Final Completion Report](docs/review_3_final_report.md)

### License

Distributed under the **MIT License**. See `LICENSE` for more information.
