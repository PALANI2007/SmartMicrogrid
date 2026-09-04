# Architecture Overview

## Technology Stack
- **Frontend**: React 18, Vite, TailwindCSS, Recharts, React-i18next
- **Backend**: FastAPI, Python 3.11, Pydantic, SQLAlchemy
- **Database**: SQLite (local embedded)
- **Machine Learning**: Scikit-Learn (Random Forest Regressor), Pandas, Joblib

## Data Flow

```mermaid
graph TD
    UI[React Frontend / Vite] <-->|Axios API Layer| API[FastAPI Backend]
    
    subgraph Backend [Backend Services]
        API <--> Services[Service Layer]
        Services <--> DB[(SQLite Database)]
    end
    
    subgraph ML [Machine Learning Pipeline]
        DB -.->|Historical Data| ML_Proc[Feature Engineering]
        ML_Proc -.-> Model[Random Forest Model]
        Model -->|Predictions| Services
    end
    
    subgraph Scheduler [Scheduler Engine]
        Services --> Engine[Constraint-Based Scheduler]
        Engine --> Metrics[Metrics Calculator]
        Metrics --> API
    end
```

## Component Roles
1. **React Frontend**: Manages application state, handles English/Tamil internationalization, and visualizes scheduler performance via Recharts. 
2. **FastAPI Backend**: Exposes strongly-typed JSON endpoints for load management, simulation runs, and ML triggering. 
3. **ML Pipeline**: A vectorized Random Forest engine that ingests historical weather/generation data and outputs 24-hour predictive vectors with confidence scores.
4. **Scheduler Engine**: Evaluates constraints (essential load protection, deadlines, battery SOC) and scores time slots based on renewable surplus to output an optimal schedule.
