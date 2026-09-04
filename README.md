# Renewable-Aware Load Scheduler for Rural Microgrid

## Intelligent Renewable-Aware Energy Management & Load Scheduling System

> **Academic Capstone Project & Smart Microgrid Reference**
>
> A data-driven renewable energy management system that combines solar generation forecasting, battery-aware scheduling, flexible load management, baseline comparison, uncertainty estimation, and explainable scheduling to improve renewable energy self-consumption in rural microgrids.

---

## 🌟 Key Features

1. **Smart Microgrid Dashboard**
   - Renewable generation monitoring.
   - Load demand visualization.
   - Battery State of Charge (SOC) monitoring.
   - Grid energy usage.
   - Renewable self-consumption metrics.
   - Renewable curtailment information.
   - Overall microgrid operating status.

2. **Machine Learning-Based Solar Forecasting**
   - Historical solar generation analysis.
   - Weather-aware feature engineering.
   - Random Forest Regression forecasting.
   - Chronological train/test split for time-series validation.
   - Naive 24-hour lag baseline comparison.
   - MAE, RMSE, and R² evaluation.
   - Dynamic forecast uncertainty estimation.
   - Prediction confidence information.

3. **Renewable-Aware Load Scheduler**
   - Forecast-driven flexible load scheduling.
   - Essential load protection.
   - Load priority handling.
   - Flexible operating windows.
   - Deadline and duration constraints.
   - Renewable availability consideration.
   - Battery-aware scheduling.
   - Conflict handling.
   - Explainable scheduling decisions.

4. **Battery-Aware Energy Management**
   - Battery capacity configuration.
   - Minimum and maximum SOC constraints.
   - Charging power limits.
   - Discharging power limits.
   - Charging/discharging efficiency.
   - Battery impact calculation during scheduling.
   - Protection against invalid battery operating states.

5. **Baseline vs Smart Scheduler Benchmark**
   - Baseline scheduler without renewable forecasts.
   - Renewable-aware smart scheduler.
   - Renewable self-consumption comparison.
   - Grid energy comparison.
   - Renewable curtailment comparison.
   - Flexible-load completion comparison.
   - Measurable improvement reporting.

6. **Edge Case & Failure Analysis**
   - Solar forecast error.
   - Low battery condition.
   - Flexible-load deadline conflicts.
   - Sudden load spikes.
   - Constraint violation prevention.
   - Scheduler response analysis.

7. **Explainable & Accessible Interface**
   - English language support.
   - Tamil language support.
   - Explainable scheduling recommendations.
   - Responsive web interface.
   - Keyboard navigation.
   - Semantic HTML.
   - ARIA accessibility support.
   - Screen-reader-friendly information.
   - Status information not dependent only on color.

---

# 🎯 Project Objective

Rural microgrids often combine renewable generation, energy storage, essential household loads, and flexible electrical loads.

Renewable generation is variable and may not always match the time at which flexible loads are operated.

The objective of this project is to develop a **renewable-aware load scheduling system** that uses solar generation forecasts and microgrid constraints to intelligently determine when flexible loads should operate.

The system attempts to:

- Increase renewable energy self-consumption.
- Reduce unnecessary grid energy usage.
- Reduce renewable energy curtailment.
- Protect essential loads.
- Respect flexible-load deadlines.
- Maintain battery operating constraints.
- Reduce unnecessary user disruption.
- Provide understandable scheduling explanations.

---

# 🏗️ System Architecture

```text
                         ┌───────────────────────────┐
                         │      Historical Data      │
                         │                           │
                         │ • Solar Generation        │
                         │ • Weather Data            │
                         │ • Load Demand             │
                         │ • Battery SOC             │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │     Data Processing       │
                         │                           │
                         │ • Data Cleaning           │
                         │ • Feature Engineering     │
                         │ • Time Features           │
                         │ • Lag Features            │
                         │ • Rolling Features        │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   Solar Forecasting ML    │
                         │                           │
                         │ Random Forest Regression  │
                         │ + Naive Baseline          │
                         └─────────────┬─────────────┘
                                       │
                              Solar Forecast
                              + Uncertainty
                                       │
                                       ▼
              ┌────────────────────────────────────────────┐
              │       Renewable-Aware Load Scheduler       │
              │                                            │
              │ • Renewable Availability                   │
              │ • Load Priority                            │
              │ • Duration                                 │
              │ • Deadline                                 │
              │ • Operating Window                         │
              │ • Battery SOC                              │
              │ • Power Constraints                        │
              └──────────────────────┬─────────────────────┘
                                     │
                                     ▼
                         ┌───────────────────────────┐
                         │     Scheduling Output     │
                         │                           │
                         │ • Smart Schedule          │
                         │ • Battery Impact          │
                         │ • Grid Energy             │
                         │ • Curtailment             │
                         │ • Self-Consumption        │
                         │ • Explanations            │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │       Web Dashboard       │
                         │                           │
                         │ • Dashboard               │
                         │ • Forecast                │
                         │ • Loads                   │
                         │ • Battery                 │
                         │ • Scheduler               │
                         │ • Comparison              │
                         │ • Experiments             │
                         │ • Alerts                  │
                         └───────────────────────────┘
