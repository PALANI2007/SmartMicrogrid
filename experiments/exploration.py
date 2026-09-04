import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_exploration():
    data_path = 'd:/Project/SmartMicrogrid/data/processed/dataset.csv'
    figures_dir = 'd:/Project/SmartMicrogrid/experiments/figures/'
    
    os.makedirs(figures_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # 1. Solar generation over time (first week)
    first_week = df.head(24 * 7)
    plt.figure(figsize=(12, 6))
    plt.plot(first_week['timestamp'], first_week['solar_generation_kw'], label='Solar (kW)', color='orange')
    plt.plot(first_week['timestamp'], first_week['load_demand_kw'], label='Load (kW)', color='blue')
    plt.title('Solar Generation vs Load (First Week)')
    plt.xlabel('Date')
    plt.ylabel('Power (kW)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'solar_vs_load_first_week.png'))
    plt.close()
    
    # 2. Daily solar profile (average across hours)
    df['hour'] = df['timestamp'].dt.hour
    hourly_avg = df.groupby('hour')[['solar_generation_kw', 'load_demand_kw', 'battery_soc_pct']].mean().reset_index()
    
    plt.figure(figsize=(10, 5))
    plt.plot(hourly_avg['hour'], hourly_avg['solar_generation_kw'], label='Avg Solar', color='orange', marker='o')
    plt.plot(hourly_avg['hour'], hourly_avg['load_demand_kw'], label='Avg Load', color='blue', marker='x')
    plt.title('Average Daily Profile (Solar vs Load)')
    plt.xlabel('Hour of Day')
    plt.ylabel('Power (kW)')
    plt.xticks(range(0, 24))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'daily_profile.png'))
    plt.close()
    
    # 3. Weather feature relationships (Correlation Matrix)
    cols = ['solar_generation_kw', 'temperature_c', 'humidity_pct', 'cloud_cover_pct', 'wind_speed_ms', 'irradiance_wm2']
    corr = df[cols].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'correlation_matrix.png'))
    plt.close()
    
    # 4. Battery SOC trend
    plt.figure(figsize=(12, 5))
    plt.plot(first_week['timestamp'], first_week['battery_soc_pct'], color='green')
    plt.title('Simulated Battery SOC Trend (First Week)')
    plt.xlabel('Date')
    plt.ylabel('State of Charge (%)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'battery_soc_trend.png'))
    plt.close()
    
    print(f"Data exploration completed. Figures saved to {figures_dir}")

if __name__ == '__main__':
    run_exploration()
