from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime
from logger import log_signal  # Import the logger

app = Flask(__name__)

# === TELEGRAM BOT SETTINGS ===
BOT_TOKEN = "7832911275:AAGqXqBScHOOMyBf8yxSmJmPxenzEBhpFNo"
CHAT_ID = "-1002526774762"

# === ROOT ENDPOINT TO AVOID 404 ON RENDER ===
@app.route('/')
def index():
    return "✅ Nova AI Webhook is running."

# === WEBHOOK ENDPOINT TO RECEIVE ALERTS ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON payload received'}), 400

    print("✅ Received Webhook Data:", data)

    # === Extract and sanitize data ===
    symbol = data.get("symbol", "Unknown")
    signal_type = data.get("type", "Unknown").upper()
    confidence = data.get("confidence", "0%")
    price = data.get("price", "N/A")
    tp = data.get("TP", "0.8%")
    sl = data.get("SL", "0.5%")

    # === Safe timestamp formatting ===
    raw_timestamp = data.get("timestamp")
    try:
        if raw_timestamp:
            dt = datetime.fromisoformat(raw_timestamp)
        else:
            dt = datetime.utcnow()
    except:
        dt = datetime.utcnow()
    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    # === Validate confidence threshold ===
    try:
        confidence_value = float(confidence.replace('%', '').strip())
    except:
        confidence_value = 0

    # === Build Telegram Message ===
    if confidence_value >= 80:
        message = f"""
📉 *New Signal From Nova AI*

• *Symbol*: `{symbol}`
• *Type*: *{signal_type}*
• *Confidence*: *{confidence}*
• *Entry Price*: `${price}`
• *TP*: `{tp}` | *SL*: `{sl}`
• *Time*: `{timestamp}`

🧠 _Signal accepted by Nova Core (≥80% confidence)_
"""
        send_telegram_message(message)

        # === Save to log (console via log_signal)
        save_trade_to_log({
            "symbol": symbol,
            "type": signal_type,
            "confidence": confidence,
            "price": price,
            "tp": tp,
            "sl": sl,
            "timestamp": timestamp
        })
    else:
        print("❌ Signal rejected (below confidence threshold)")

    return jsonify({'status': 'ok'}), 200

# === FUNCTION TO SEND MESSAGE TO TELEGRAM ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        print("✅ Telegram response:", response.status_code, response.text)
        return response.json()
    except Exception as e:
        print("Telegram error:", e)

# === FUNCTION TO LOG TRADES (Render-friendly) ===
def save_trade_to_log(trade_data):
    try:
        log_signal({
            "timestamp": trade_data.get("timestamp"),
            "type": trade_data.get("type"),
            "symbol": trade_data.get("symbol"),
            "price": trade_data.get("price"),
            "confidence": trade_data.get("confidence"),
            "TP": trade_data.get("tp"),
            "SL": trade_data.get("sl"),
        })
        print("✅ Trade logged successfully.")
    except Exception as e:
        print("❌ Logging failed:", e)

# === PORT BINDING FOR RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
