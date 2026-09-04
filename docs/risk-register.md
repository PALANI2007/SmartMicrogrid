# Risk Register

| Risk ID | Risk | Likelihood (H/M/L) | Impact (H/M/L) | Mitigation | Status |
|---------|------|--------------------|----------------|------------|--------|
| R01 | Forecast inaccuracy in unexpected weather | M | H | Utilize confidence intervals and maintain a larger battery buffer during volatile seasons. | Active |
| R02 | Battery failure/degradation | L | H | Enforce strict minimum/maximum SOC bounds (20%-95%) in software. Regular hardware maintenance. | Active |
| R03 | Sensor/data communication failure | M | M | Implement fallback logic using historical averages if real-time telemetry fails. | Active |
| R04 | User rejection of recommendations | M | M | Use Explainable AI (XAI) text to build trust. Provide manual override capabilities. | Active |
| R05 | Incorrect constraint configuration | H | M | Implement input validation in the UI to prevent logically impossible time windows. | Active |
| R06 | Unexpected load spikes | M | H | Real-time monitoring with auto-shedding of flexible loads if the grid frequency/SOC drops dangerously. | Active |
| R07 | Grid outage during peak scheduling | L | H | Assume islanded mode as default in scheduling logic; treat grid as a secondary backup only. | Active |
| R08 | Data privacy concerns | L | L | Localize data storage (SQLite on device); avoid cloud telemetry unless explicitly opted in. | Active |
| R09 | Software bugs in scheduler | L | H | Comprehensive unit testing and "dry run" simulations before applying schedules to physical relays. | Active |
| R10 | Seasonal model drift | M | M | Retrain the ML model periodically (e.g., quarterly) with new telemetry data. | Active |
