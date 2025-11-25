import pandas as pd
from sklearn.linear_model import LinearRegression
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
import sys
import json

def main():
    # --- CONFIGURATION ---
    # 1 = Growth (Day 0-150)
    # 2 = Stable (Day 151-180)
    # 3 = Decline (Day 181-220)
    scatter_scope = 3
    
    # 1. Find the newest Excel file
    folder_path = r'/home/lenovo/Downloads'
    files = glob.glob(os.path.join(folder_path, '*.xlsx'))
    
    if not files:
        print("No Excel files found.")
        return

    latest_file = max(files, key=os.path.getmtime)
    print(f"Processing file: {latest_file}")

    plot_dir = './plots'
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
        print(f"Created directory: {plot_dir}")

    # 2. Read and Clean Data
    df = pd.read_excel(latest_file, sheet_name='Plots Data', header=3)
    df = df.dropna(how='all')
    df['Days'] = pd.to_numeric(df['Days'], errors='coerce')
    df = df.dropna(subset=['Days'])

    # Identify current max day for file naming/logging
    max_days = int(max(df['Days']))

    # --- SCOPE LOGIC (For Demand Regression) ---
    if scatter_scope == 1:
        scope_start, scope_end = 0, 150
    elif scatter_scope == 2:
        scope_start, scope_end = 151, 180
    elif scatter_scope == 3:
        scope_start, scope_end = 181, 220
    else:
        scope_start, scope_end = 0, 300 # Fallback

    # Create the specific dataset for regression based on scope
    mask = (df['Days'] >= scope_start) & (df['Days'] <= scope_end)
    df_scope = df.loc[mask]

    # --- REGRESSION (On Scoped Data) ---
    # We only run regression if we have data in this scope
    model = LinearRegression()
    
    if not df_scope.empty:
        X_scope = df_scope[['Days']]
        Y_scope = df_scope[['Jobs accepted 1']] # Was Unnamed: 2
        
        model.fit(X_scope, Y_scope)
        
        intercept = model.intercept_
        coefficient_1 = model.coef_[0]
        
        # Use .item() or float() to ensure we are formatting a number, not an array
        # This fixes the "Unknown format code 'f' for object of type 'str'" error
        if isinstance(intercept, (np.ndarray, np.generic)):
             intercept = intercept.item()
        if isinstance(coefficient_1, (np.ndarray, np.generic)):
             coefficient_1 = coefficient_1.item()

        print(f"Scope {scatter_scope} ({scope_start}-{scope_end}) Regression:")
        print(f"Intercept: {intercept:.4f}")
        print(f"Slope: {coefficient_1:.4f}")
    else:
        print(f"No data yet for Scope {scatter_scope}. Skipping regression.")
        intercept = 0.0
        coefficient_1 = 0.0

    # --- RECENT DATA (For Operational Plots - Last 50 Days) ---
    if len(df) > 50:
        recent_df = df.tail(50)
    else:
        recent_df = df

    X_recent = recent_df[['Days']]
    
    # Map variables for plotting
    lead_time_recent = recent_df['Lead time 1']
    completed_jobs_recent = recent_df['Jobs out 1']
    
    kit_in_queue1_recent = recent_df['kits 1']
    kit_in_queue2_recent = recent_df['kits 2']
    kit_in_queue3_recent = recent_df['kits 3']
    
    util1_recent = recent_df['Utilization 1']
    util2_recent = recent_df['Utilization 2']
    util3_recent = recent_df['Utilization 3']

    # --- PLOTTING OPERATIONAL METRICS (Last 50 Days) ---

    # 1. Lead Time
    plt.figure()
    plt.plot(X_recent, lead_time_recent, color='pink', label=f'Latest: {lead_time_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Lead Time')
    plt.title(f'Days {max_days-50}-{max_days} Lead Time')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_4_lead_time_plot.png')
    plt.close()

    # 2. Completed Jobs
    plt.figure()
    plt.plot(X_recent, completed_jobs_recent, color='orange', label=f'Latest: {completed_jobs_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Completed Jobs')
    plt.title(f'Days {max_days-50}-{max_days} Completed Jobs')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_5_completed_jobs_plot.png')
    plt.close()

    # 3. Kits in Queue
    plt.figure()
    plt.plot(X_recent, kit_in_queue1_recent, color='green', label=f'S1 Latest: {kit_in_queue1_recent.iloc[-1]}')
    plt.plot(X_recent, kit_in_queue2_recent, color='red', label=f'S2 Latest: {kit_in_queue2_recent.iloc[-1]}')
    plt.plot(X_recent, kit_in_queue3_recent, color='purple', label=f'S3 Latest: {kit_in_queue3_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Avg Kits In Queue')
    plt.title(f'Days {max_days-50}-{max_days} Avg Kits Queue')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_3_avg_kit_plot.png')
    plt.close()

    # 4. Utilization
    plt.figure()
    plt.plot(X_recent, util1_recent, color='green', label=f'S1 Latest: {util1_recent.iloc[-1]}')
    plt.plot(X_recent, util2_recent, color='red', label=f'S2 Latest: {util2_recent.iloc[-1]}')
    plt.plot(X_recent, util3_recent, color='purple', label=f'S3 Latest: {util3_recent.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Utilization')
    plt.title(f'Days {max_days-50}-{max_days} Utilization')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_1_utilization_plot.png')
    plt.close()

    # --- DEMAND PLOT (Scoped) ---
    if not df_scope.empty:
        # Create a trendline range matching the scope
        future_X = np.arange(scope_start, scope_end + 1).reshape(-1, 1)
        equation = f'y = {coefficient_1:.4f}x + {intercept:.4f}'

        plt.figure()
        # Plot the ACTUAL data dots for the scope
        # Get the latest value from the Y_scope Series. 
        # Note: Y_scope is a DataFrame because of the double bracket [['Jobs accepted 1']] selection earlier
        # We use .iloc[-1].item() to get the scalar value safely.
        latest_demand_val = Y_scope.iloc[-1].item()
        
        plt.scatter(X_scope, Y_scope, color='blue', label=f'Demand, latest = {latest_demand_val:.2f}')
        # Plot the REGRESSION line for the scope
        plt.plot(future_X, model.predict(future_X), color='red', label=f'Trend: {equation}')

        plt.xlabel('Day Number')
        plt.ylabel('Predicted Demand')
        plt.title(f'Demand Forecast (Scope {scatter_scope}: Days {scope_start}-{scope_end})')
        plt.legend()
        plt.savefig(f'./plots/d{max_days}_2_demand_plot.png')
        plt.close()
    else:
        print(f"Skipping Demand Plot: No data for Scope {scatter_scope}")

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
