from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)

# === TELEGRAM BOT SETTINGS ===
BOT_TOKEN = "7832911275:AAGqXqBScHOOMyBf8yxSmJmPxenzEBhpFNo"
CHAT_ID = "-1002526774762"
LOG_FILE = "trade_log.json"

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
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())
    price = data.get("price", "N/A")
    tp = data.get("TP", "0.8%")
    sl = data.get("SL", "0.5%")

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

        # === Save to log ===
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

# === FUNCTION TO SAVE TRADES ===
def save_trade_to_log(trade_data):
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                log = json.load(f)
        else:
            log = []
        log.append(trade_data)
        with open(LOG_FILE, 'w') as f:
            json.dump(log, f, indent=2)
        print("✅ Trade saved to log.")
    except Exception as e:
        print("Log write error:", e)

# === PORT BINDING FOR RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
