# Renewable-Aware Load Scheduler for Rural Microgrid

## 📌 Project Overview

The **Renewable-Aware Load Scheduler for Rural Microgrid** is a data-driven smart energy management system designed to improve the utilization of renewable energy in rural microgrids.

The system uses **solar generation forecasting, load flexibility, battery status, load priorities, and scheduling constraints** to determine suitable operating times for flexible electrical loads.

Instead of operating flexible loads at fixed times, the proposed system attempts to shift them toward periods where renewable energy availability is higher.

The main objective is:

> **Increase renewable energy self-consumption while maintaining essential loads, battery constraints, user deadlines, and operational requirements.**

---

## 🎯 Objectives

The major objectives of this project are:

- Forecast short-term solar power generation.
- Analyze historical renewable generation and load demand.
- Identify essential and flexible electrical loads.
- Schedule flexible loads according to renewable availability.
- Protect essential loads from unnecessary interruption.
- Manage battery charging and discharging constraints.
- Compare a traditional baseline scheduler with the renewable-aware scheduler.
- Reduce grid energy dependency.
- Reduce renewable energy curtailment.
- Improve renewable self-consumption.
- Handle forecast uncertainty and scheduling conflicts.
- Provide an explainable scheduling decision for each load.
- Provide an accessible web-based dashboard.
- Support both **English and Tamil** interfaces.
- Evaluate the system using measurable experiments.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │     Historical Data     │
                    │                         │
                    │ Solar Generation        │
                    │ Weather Data            │
                    │ Load Demand             │
                    │ Battery SOC             │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Data Processing      │
                    │                         │
                    │ Cleaning                 │
                    │ Feature Engineering      │
                    │ Validation              │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Solar Forecasting Model │
                    │                         │
                    │ Random Forest           │
                    │ Regression              │
                    └────────────┬────────────┘
                                 │
                    Solar Forecast + Uncertainty
                                 │
                                 ▼
              ┌────────────────────────────────────┐
              │ Renewable-Aware Load Scheduler    │
              │                                    │
              │ • Load Priority                    │
              │ • Deadline                          │
              │ • Duration                          │
              │ • Battery Constraints               │
              │ • Renewable Availability             │
              │ • Essential Load Protection         │
              └───────────────┬────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Scheduling Results   │
                   │                      │
                   │ Smart Schedule       │
                   │ Battery Impact       │
                   │ Grid Energy          │
                   │ Curtailment          │
                   │ Self-Consumption     │
                   └────────────┬─────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │      Web Dashboard     │
                    │                        │
                    │ Forecast               │
                    │ Loads                  │
                    │ Battery                │
                    │ Scheduler              │
                    │ Comparison             │
                    │ Experiments            │
                    └────────────────────────┘
