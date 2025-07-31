# ===========================================================
# ANALYZER LOOP SCRIPT
#
# This script runs the analyze_data module every 60 seconds.
# It uses the current Python interpreter to call `core.analyze_data`
# and is useful for keeping data analysis updated continuously.
# ===========================================================

import subprocess
import time
import sys

print("Analyzer loop started. Running every 60 seconds.")

while True:
    try:
        print("Running analysis...")
        subprocess.run([sys.executable, "-m", "core.analyze_data"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during analysis: {e}")

    time.sleep(60)  # Wait for 60 seconds before the next run
