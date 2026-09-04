# Data Schema & Generation Methodology

This document details the generation process and schema of the 6-month realistic hourly dataset used in this 50% milestone.

## Pipeline Architecture
1. **Raw Generation (`data/generate_data.py`)**: A script generates a robust 6-month hourly time series spanning `2024-01-01` to `2024-06-30`.
2. **Raw Storage**: Stored in `data/raw/dataset.csv`.
3. **Processing**: Outliers and missing values are injected and then handled (forward/backward fill, median replacement) to demonstrate data resilience.
4. **Processed Storage**: Stored in `data/processed/dataset.csv`.

## Data Schema

The dataset includes 4,368 hourly records with the following features:

| Column Name | Type | Description |
|-------------|------|-------------|
| `timestamp` | Datetime | Hourly timestamp (YYYY-MM-DD HH:MM:SS) |
| `temperature_c` | Float | Ambient temperature (°C) simulating tropical/arid climate with daily cycles |
| `humidity_pct` | Float | Relative humidity (%), inversely correlated with temperature |
| `cloud_cover_pct` | Float | Cloud cover percentage (0-100) affecting irradiance |
| `wind_speed_ms` | Float | Wind speed in meters per second |
| `irradiance_wm2` | Float | Solar irradiance (W/m²), calculated based on time of day and cloud cover |
| `solar_generation_kw` | Float | Output of a simulated 10kW solar array, derived from irradiance with temperature derating |
| `load_demand_kw` | Float | Aggregated uncontrolled load demand simulating a small rural community |
| `battery_soc_pct` | Float | Simulated battery state-of-charge for naive rolling operation (baseline tracking) |

## Key Characteristics
- **Realism**: Uses diurnal cycles for temperature and irradiance.
- **Noise Injection**: Includes gaussian noise to simulate sensor inaccuracy.
- **Robustness**: Deliberately injects `NaN` values and extreme outliers, which are successfully imputed during processing.
