"""
This script tests the anomaly detection pipeline by:
1. Importing the anomaly detection function.
2. Running the detection on the latest sensor data.
3. Logging any detected anomalies into a CSV file.

Used during development to verify that detection and logging work as expected.
"""

from core.detect_anomalies import detect_anomalies
from core.log_anomalies import log_anomalies_to_csv

# Run anomaly detection
anomalies = detect_anomalies()

# Save anomalies to CSV if any were found
log_anomalies_to_csv(anomalies)

# Output the detected anomalies
print("Detected anomalies:", anomalies)
