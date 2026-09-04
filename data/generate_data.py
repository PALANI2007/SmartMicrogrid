import pandas as pd
import numpy as np
from datetime import datetime
import os

# Ensure directories exist
os.makedirs('d:/Project/SmartMicrogrid/data/raw', exist_ok=True)
os.makedirs('d:/Project/SmartMicrogrid/data/processed', exist_ok=True)
os.makedirs('d:/Project/SmartMicrogrid/experiments/figures', exist_ok=True)

# Fixed random seed for reproducibility
np.random.seed(42)

def generate_hourly_data():
    dates = pd.date_range(start='2024-01-01', end='2024-06-30 23:00:00', freq='h')
    num_rows = len(dates)

    temp_c = np.zeros(num_rows)
    humidity_pct = np.zeros(num_rows)
    cloud_cover_pct = np.random.uniform(0, 100, num_rows)
    wind_speed_ms = np.random.uniform(0, 10, num_rows)
    irradiance_wm2 = np.zeros(num_rows)
    solar_gen = np.zeros(num_rows)
    load_demand_kw = np.zeros(num_rows)
    battery_soc_pct = np.zeros(num_rows)

    current_soc = 50.0 # Start at 50%

    for i, dt in enumerate(dates):
        hour = dt.hour
        month = dt.month
        
        # Temperature profile (15-40 C in Tamil Nadu rural areas)
        base_temp = 25 + (month - 1) * 1.5
        temp_c[i] = base_temp + 5 * np.sin((hour - 8) * np.pi / 12) + np.random.normal(0, 1)
        temp_c[i] = np.clip(temp_c[i], 15, 40)
        
        # Humidity profile
        humidity_pct[i] = 100 - (temp_c[i] - 15) * 2 + np.random.normal(0, 5)
        humidity_pct[i] = np.clip(humidity_pct[i], 30, 95)
        
        cc = cloud_cover_pct[i]
        
        # Irradiance and Solar Generation
        if 6 <= hour <= 19:
            # Bell curve for irradiance during the day
            base_irrad = np.sin((hour - 6) * np.pi / 13) * 1000
            # Cloud cover reduces irradiance by up to 70%
            irrad = base_irrad * (1 - 0.7 * (cc / 100.0))
            # Add some noise
            irradiance_wm2[i] = max(0, irrad + np.random.normal(0, 50))
        else:
            irradiance_wm2[i] = 0

        # Assume 5kW capacity solar panel with 15% efficiency
        # generation = irradiance * area * efficiency
        # Simplify: generation (kW) = irradiance (W/m2) * 0.005
        solar_gen[i] = irradiance_wm2[i] * 0.005
        
        # Load demand (simulated generic load)
        # Higher in the evening (18-22) and morning (7-9)
        base_load = 1.0
        if 7 <= hour <= 9:
            base_load += np.random.uniform(1.0, 3.0)
        elif 18 <= hour <= 22:
            base_load += np.random.uniform(2.0, 5.0)
        else:
            base_load += np.random.uniform(0.5, 1.5)
            
        load_demand_kw[i] = base_load

        # Simulate Battery SOC trace (10kWh battery)
        surplus = solar_gen[i] - load_demand_kw[i]
        battery_kwh = (current_soc / 100.0) * 10.0
        if surplus > 0:
            battery_kwh += min(surplus, 3.0) * 0.95 # charge
        else:
            battery_kwh += max(surplus, -3.0) / 0.95 # discharge
            
        battery_kwh = np.clip(battery_kwh, 2.0, 9.5) # 20% to 95%
        current_soc = (battery_kwh / 10.0) * 100
        battery_soc_pct[i] = current_soc

    # Introduce some artificial missing values and outliers for the raw dataset
    raw_temp = temp_c.copy()
    raw_solar = solar_gen.copy()
    
    # 1% missing values in temp
    missing_idx = np.random.choice(num_rows, int(num_rows * 0.01), replace=False)
    raw_temp[missing_idx] = np.nan
    
    # Negative outlier in solar (impossible)
    outlier_idx = np.random.choice(num_rows, int(num_rows * 0.005), replace=False)
    raw_solar[outlier_idx] = -5.0

    raw_df = pd.DataFrame({
        'timestamp': dates,
        'solar_generation_kw': raw_solar,
        'temperature_c': raw_temp,
        'humidity_pct': humidity_pct,
        'cloud_cover_pct': cloud_cover_pct,
        'wind_speed_ms': wind_speed_ms,
        'irradiance_wm2': irradiance_wm2,
        'load_demand_kw': load_demand_kw,
        'battery_soc_pct': battery_soc_pct
    })
    
    raw_df.to_csv('d:/Project/SmartMicrogrid/data/raw/dataset.csv', index=False)
    
    # Processing:
    # 1. Forward fill missing temps
    # 2. Clip solar_generation to 0
    proc_df = raw_df.copy()
    proc_df['temperature_c'] = proc_df['temperature_c'].ffill().bfill()
    proc_df['solar_generation_kw'] = proc_df['solar_generation_kw'].clip(lower=0)
    
    proc_df.to_csv('d:/Project/SmartMicrogrid/data/processed/dataset.csv', index=False)

def generate_static_data():
    loads_data = [
        ['Refrigerator', 'essential', 0.3, 24, '', '', 'high', 'Continuous refrigeration'],
        ['Medical Equipment', 'essential', 0.8, 24, '', '', 'high', 'Critical medical device'],
        ['Water Pump', 'flexible', 1.5, 2, '08:00', '18:00', 'high', 'Daily water pumping'],
        ['Washing Machine', 'flexible', 0.8, 1, '09:00', '20:00', 'medium', 'Laundry'],
        ['Water Heater', 'flexible', 2.0, 1, '10:00', '17:00', 'medium', 'Hot water'],
        ['EV Charging', 'flexible', 3.3, 3, '18:00', '07:00', 'high', 'Electric vehicle charge']
    ]
    df_loads = pd.DataFrame(loads_data, columns=['name', 'load_type', 'power_kw', 'duration_hours', 'earliest_start', 'latest_finish', 'priority', 'description'])
    df_loads.to_csv('d:/Project/SmartMicrogrid/data/processed/loads.csv', index=False)

    battery_data = {
        'capacity_kwh': [10],
        'initial_soc': [50.0],
        'minimum_soc': [20.0],
        'maximum_soc': [95.0],
        'max_charge_kw': [3.0],
        'max_discharge_kw': [3.0],
        'charging_efficiency': [0.95],
        'discharging_efficiency': [0.95]
    }
    df_battery = pd.DataFrame(battery_data)
    df_battery.to_csv('d:/Project/SmartMicrogrid/data/processed/battery.csv', index=False)

if __name__ == '__main__':
    generate_hourly_data()
    generate_static_data()
    print("Data generation script completed successfully. Created raw and processed datasets.")
