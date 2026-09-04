# User Guide

Welcome to the Renewable Microgrid Load Scheduler. This tool optimizes the operation of flexible appliances (loads) in rural microgrids by aligning their usage with peak solar generation, thereby reducing grid dependency and battery wear.

## 1. Getting Started
To start the application locally:
1. Ensure the Python backend is running (`uvicorn app.main:app --reload`).
2. Ensure the Vite frontend is running (`npm run dev`).
3. Open `http://localhost:5173` in your browser.

## 2. Navigating the Application

### Dashboard
The main screen provides a live overview of your microgrid:
- **Current Solar & Load**: Real-time kW metrics.
- **Battery SOC**: State of Charge of your energy storage.
- **Energy Mix Pie Chart**: Shows your ratio of renewable self-consumption vs grid dependency.
- **Active Loads Table**: A list of currently running or scheduled appliances.

### Forecast
View the Machine Learning model's 24-hour predictions for solar generation. The shaded area in the chart represents the model's confidence bounds.

### Loads Management
Here you can configure the appliances in your microgrid.
- **Essential Loads**: Items like medical equipment or basic lighting that must run 24/7.
- **Flexible Loads**: Items like water pumps or EV chargers. You can set an `Earliest Start` and `Latest Finish` time, and the smart scheduler will automatically find the best time to run them based on the weather forecast.

### Scheduler
Run the AI scheduler engine. It will evaluate all your flexible loads against the solar forecast and battery state, and output an optimized schedule. It provides clear, human-readable explanations for why it chose a specific time slot, or why a load could not be scheduled (e.g., due to a deadline conflict).

### Battery Configuration
Modify the physical parameters of your energy storage system, including total capacity (kWh), maximum charge rates, and minimum safety SOC limits.

### Comparison & Experiments
Run simulations comparing a "Baseline" naive scheduler against the "Optimized" smart scheduler to see exactly how much energy and money you are saving.

## 3. Localization
Click the `English` or `தமிழ்` button in the top navigation bar at any time to switch the application's language instantly.
