# logger.py

import csv
import os
from datetime import datetime

LOG_FILE = "trade_log.csv"

def log_signal(data):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True) if '/' in LOG_FILE else None
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "type", "symbol", "price",
                "confidence", "TP", "SL"
            ])
        writer.writerow([
            data.get("timestamp", datetime.utcnow().isoformat()),
            data.get("type", "N/A"),
            data.get("symbol", "N/A"),
            data.get("price", "N/A"),
            data.get("confidence", "0%"),
            data.get("TP", "N/A"),
            data.get("SL", "N/A"),
        ])
