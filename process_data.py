import pandas as pd
from sklearn.linear_model import LinearRegression
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import json

def main():
    # 1. Find the newest Excel file
    folder_path = r'/home/lenovo/Downloads'
    files = glob.glob(os.path.join(folder_path, '*.xlsx'))
    
    if not files:
        print("No Excel files found.")
        return

    latest_file = max(files, key=os.path.getmtime) # Changed to getmtime for safety
    print(f"Processing file: {latest_file}")

    plot_dir = './plots'
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
        print(f"Created directory: {plot_dir}")

    # 2. Read the data
    # Using header=3 is safer given your previous file structure issues
    df = pd.read_excel(latest_file, sheet_name='Plots Data', header=3)
    
    # Clean data (drop completely empty rows)
    df = df.dropna(how='all')
    
    # Rename columns to match your logic (optional but helps readability)
    # Assuming column positions based on your previous code:
    # 'Days' is usually auto-detected if header=3 is used.
    
    # Ensure numeric data for regression
    df['Days'] = pd.to_numeric(df['Days'], errors='coerce')
    df = df.dropna(subset=['Days'])

    # --- FULL DATASETS (For Regression) ---
    X = df[['Days']] 
    Y = df['Jobs accepted 1'] # Was Unnamed: 2
    max_days = int(max(df['Days']))

    # --- RECENT DATASETS (For Visual Plots - Last 50 Days) ---
    # We verify if we have more than 50 days. If so, we slice the last 50.
    if len(df) > 50:
        recent_df = df.tail(50)
    else:
        recent_df = df

    X_recent = recent_df[['Days']]
    
    # Map variables to the RECENT dataframe for plotting
    lead_time_recent = recent_df['Lead time 1'] # Was Unnamed: 14
    completed_jobs_recent = recent_df['Jobs out 1'] # Was Completed jobs
    
    kit_in_queue1_recent = recent_df['kits 1'] # Was Station 1
    kit_in_queue2_recent = recent_df['kits 2'] # Was Station 2
    kit_in_queue3_recent = recent_df['kits 3'] # Was Station 3
    
    util1_recent = recent_df['Utilization 1'] # Was Unnamed: 4
    util2_recent = recent_df['Utilization 2'] # Was Unnamed: 7
    util3_recent = recent_df['Utilization 3'] # Was Unnamed: 10

    # --- REGRESSION MATH (Uses FULL History X & Y) ---
    model = LinearRegression()
    model.fit(X, Y)
    
    intercept = model.intercept_
    coefficient_1 = model.coef_[0]

    print(f"Intercept: {intercept}")
    print(f"Coefficient 1: {coefficient_1}")
    print(f"Max Days: {max_days}")

    # --- PLOTTING (Uses RECENT Data) ---

    # 1. Lead Time (Recent)
    plt.figure()
    plt.plot(X_recent, lead_time_recent, color='pink', label=f'Latest: {lead_time_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Lead Time')
    plt.title(f'Days {max_days - 50}-{max_days} Lead Time')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_4_lead_time_plot.png')
    plt.close()

    # 2. Completed Jobs (Recent)
    plt.figure()
    plt.plot(X_recent, completed_jobs_recent, color='orange', label=f'Latest: {completed_jobs_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Completed Jobs')
    plt.title(f'Days {max_days - 50}-{max_days} Completed Jobs')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_5_completed_jobs_plot.png')
    plt.close()

    # 3. Average Kits in Queue (Recent)
    plt.figure()
    plt.plot(X_recent, kit_in_queue1_recent, color='green', label=f'S1 Latest: {kit_in_queue1_recent.iloc[-1]}')
    plt.plot(X_recent, kit_in_queue2_recent, color='red', label=f'S2 Latest: {kit_in_queue2_recent.iloc[-1]}')
    plt.plot(X_recent, kit_in_queue3_recent, color='purple', label=f'S3 Latest: {kit_in_queue3_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Avg Kits In Queue')
    plt.title(f'Days {max_days - 50}-{max_days} Avg Kits Queue (Last 50 Days)')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_3_avg_kit_plot.png')
    plt.close()

    # 4. Utilization (Recent)
    plt.figure()
    plt.plot(X_recent, util1_recent, color='green', label=f'S1 Latest: {util1_recent.iloc[-1]}')
    plt.plot(X_recent, util2_recent, color='red', label=f'S2 Latest: {util2_recent.iloc[-1]}')
    plt.plot(X_recent, util3_recent, color='purple', label=f'S3 Latest: {util3_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Utilization')
    plt.title(f'Days {max_days - 50}-{max_days} Utilization')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_1_utilization_plot.png')
    plt.close()

    # --- DEMAND PLOT (Uses FULL History X & Y) ---
    
    future_X = np.arange(0, 151).reshape(-1, 1)
    equation = f'y = {coefficient_1:.4f}x + {intercept:.4f}'

    plt.figure()
    plt.scatter(X, Y, color='blue', label=f'Actual Demand')
    plt.plot(future_X, model.predict(future_X), color='red', label=f'Trend: {equation}')

    plt.xlabel('Day Number')
    plt.ylabel('Predicted Demand')
    plt.title('Demand Forecast: Full History')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_2_demand_plot.png')
    plt.close()

    # Save state
    sim_data = {
        "current_day": int(max_days),
        "status": "Success"
    }

    with open("sim_state.json", "w") as f:
        json.dump(sim_data, f)
        
    print(f"Saved simulation state (Day {max_days}) to sim_state.json")

if __name__ == "__main__":
    main()