import pandas as pd
from sklearn.linear_model import LinearRegression
import glob
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import sys

def main():
    # start_day = 0
    # end_day = 150
    # args = False

    # if (sys.argv[1].isdigit() and sys.argv[2].isdigit()):
    #     args = True
    #     start_day = int(sys.argv[1])
    #     end_day = int(sys.argv[2])

    # 1. Find the newest Excel file in a folder
    folder_path = r'/home/lenovo/Downloads'
    files = glob.glob(os.path.join(folder_path, '*.xlsx'))
    latest_file = max(files, key=os.path.getctime)

    print(f"Processing file: {latest_file}")

    plot_dir = './plots'
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
        print(f"Created directory: {plot_dir}")


    # 2. Read the data
    # Replace 'Sheet1', 'TargetCol', and 'InputCol' with your actual names
    df = pd.read_excel(latest_file, sheet_name='Plots Data')

    # Get rid of the first three rows. They're kinda weird.
    # df = df.iloc[3:]

    # Clean data (drop empty rows for regression)
    df = df.dropna(subset=['Unnamed: 2', 'Days'])

    X = df[['Days']] # Double brackets for 2D array
    Y = df['Unnamed: 2']
    util1 = df['Unnamed: 4']
    util2 = df['Unnamed: 7']
    util3 = df['Unnamed: 10']
    kit_in_queue1 = df['Station 1']
    kit_in_queue2 = df['Station 2']
    kit_in_queue3 = df['Station 3']
    lead_time = df['Unnamed: 14']
    completed_jobs = df['Completed jobs']
    max_days = max(df['Days'])

    # 3. Perform Regression
    model = LinearRegression()
    model.fit(X, Y)

    # 4. Get Coefficients
    intercept = model.intercept_
    coefficient_1 = model.coef_[0]

    print(f"Intercept: {intercept}")
    print(f"Coefficient 1: {coefficient_1}")
    print(f"Max Days: {max_days}")


    demand_forecast_12 = intercept + coefficient_1 * (max_days + 12)
    print(f"Demand Forecast for 12 days: {demand_forecast_12}")


    plt.plot(X, util1, color='green', label=f'S1 latest = {util1.iloc[-1]}')
    plt.plot(X, util2, color='red', label=f'S2 latest = {util2.iloc[-1]}')
    plt.plot(X, util3, color='purple', label=f'S3 latest = {util3.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Utilization')
    plt.title(f'Day 0-{max_days} Utilization (lower is better)')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_1_utilization_plot.png')
    # # plt.show()
    plt.close()


    plt.plot(X, kit_in_queue1, color='green', label=f'S1 latest = {kit_in_queue1.iloc[-1]}')
    plt.plot(X, kit_in_queue2, color='red', label=f'S2 latest = {kit_in_queue2.iloc[-1]}')
    plt.plot(X, kit_in_queue3, color='purple', label=f'S3 latest = {kit_in_queue3.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Avg Kits In Queue')
    plt.title(f'Day 0-{max_days} Avg Kits In Queue (lower is better)')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_3_avg_kit_plot.png')
    # plt.show()
    plt.close()


    # Let's plot the data and the regression line
    # plt.scatter(X, Y, color='blue', label='Data Points')
    plt.plot(X, lead_time, color='pink', label=f'Lead Time latest = {lead_time.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Lead Time')
    plt.title(f'Day 0-{max_days} Lead Time')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_4_lead_time_plot.png')
    # plt.show()
    plt.close()

    # Let's plot the data and the regression line
    # plt.scatter(X, Y, color='blue', label='Data Points')
    plt.plot(X, completed_jobs, color='orange', label=f'Completed Jobs latest {completed_jobs.iloc[-1]}')
    plt.xlabel('Days')
    plt.ylabel('Completed Jobs')
    plt.title(f'Day 0-{max_days} Completed Jobs (higher is better)')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_5_completed_jobs_plot.png')
    # plt.show()
    plt.close()

    # 1. Capture the values
    slope = model.coef_[0]
    intercept = model.intercept_

    # 1. Create a "Future" X timeline (e.g., Day 0 to Day 150)
    # This lets us draw the line past the current day
    future_X = np.arange(0, 151).reshape(-1, 1)

    # 2. Create a label string
    # The 'f' string allows us to insert the variables directly
    equation = f'y = {slope:.4f}x + {intercept:.4f}'

    # 3. Plot
    plt.scatter(X, Y, color='blue', label=f'Demand latest = {Y.iloc[-1]}')
    # Pass the equation into the label here:
    plt.plot(future_X, model.predict(future_X), color='red', label=f'Trend: {equation}')

    plt.legend() # This will now show the line color next to the equation



    plt.xlabel('Day Number')
    plt.ylabel('Predicted Demand')
    plt.title('Demand Forecast: Day 0 to 150')
    plt.legend()
    plt.savefig(f'./plots/d{max_days}_2_demand_plot.png')
    # plt.show()
    plt.close()


    print(kit_in_queue1.iloc[-1])