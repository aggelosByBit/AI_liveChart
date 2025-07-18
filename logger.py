import csv
import os
from datetime import datetime

LOG_FILE = "signals.csv"

def log_signal(data):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True) if os.path.dirname(LOG_FILE) else None
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "type", "symbol", "price", "confidence", "TP", "SL"])

        writer.writerow([
            data.get("timestamp"),
            data.get("type"),
            data.get("symbol"),
            data.get("price"),
            data.get("confidence"),
            data.get("TP"),
            data.get("SL"),
        ])
