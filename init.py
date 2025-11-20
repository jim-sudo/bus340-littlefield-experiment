import pyautogui_usage
import process_data
import subprocess  # <--- The library for running external scripts
import sys

print("--- Step 1: Running PyAutoGUI ---")
pyautogui_usage.main()

print("--- Step 2: Processing Excel Data ---")
process_data.main()

print("--- Step 3: Launching Discord Bot ---")
# This runs 'python discord_bot.py' just like you would in the terminal
# sys.executable ensures it uses the same Python environment (venv) as this script
subprocess.run([sys.executable, "discord_bot.py"])

print("--- Pipeline Complete! ---")