# logger.py
import csv
import os
from datetime import datetime

LOG_FILE = "logs/signals.csv"

def log_signal(data, write_to_file=False):
    # Print to console for Render logging
    print(f"[SIGNAL] {datetime.utcnow().isoformat()} | {data}")

    if write_to_file:
        os.makedirs("logs", exist_ok=True)
        file_exists = os.path.isfile(LOG_FILE)

        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(["timestamp", "type", "symbol", "price", "confidence", "TP", "SL"])

            writer.writerow([
                data.get("timestamp", datetime.utcnow().isoformat()),
                data.get("type", "N/A"),
                data.get("symbol", "N/A"),
                data.get("price", "N/A"),
                data.get("confidence", "N/A"),
                data.get("TP", "N/A"),
                data.get("SL", "N/A"),
            ])
