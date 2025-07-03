from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)
LOG_FILE = "trade_log.csv"

@app.route("/")
def home():
    return "Nova AI Flask backend is running."

@app.route("/log-signal", methods=["POST"])
def log_signal():
    data = request.json
    if not data:
        return jsonify({"status": "fail", "message": "No JSON received"}), 400

    # Append signal to CSV
    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("symbol", ""),
            data.get("timeframe", ""),
            data.get("type", ""),
            data.get("entry", ""),
            data.get("tp", ""),
            data.get("sl", "")
        ])

    return jsonify({"status": "success", "message": "Signal logged."}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
