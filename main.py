from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime
from logger import log_signal  # Local logger

app = Flask(__name__)

# === TELEGRAM BOT SETTINGS ===
BOT_TOKEN = "7832911275:AAGqXqBScHOOMyBf8yxSmJmPxenzEBhpFNo"
CHAT_ID = "-1002526774762"

# === ROOT ENDPOINT (health check) ===
@app.route('/')
def index():
    return "✅ Nova AI Webhook is running."

# === WEBHOOK: Receives signal from TradingView ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON payload received'}), 400

    print("✅ Received Webhook Data:", data)

    # === STEP 1: Forward to AI Brain ===
    try:
        ai_response = requests.post(
            "https://1d901c6e-e756-47a9-a5c5-98809de105a7-00-3supnbl570r0e.janeway.replit.dev/webhook",
            json=data,
            timeout=5
        )
        ai_json = ai_response.json()
        print("🧠 AI Response:", ai_json)
    except Exception as e:
        print("❌ Failed to connect to AI Brain:", e)
        return jsonify({"error": "AI Brain unreachable"}), 502

    # === STEP 2: Check AI Decision ===
    if ai_json.get("final_decision") != "forwarded":
        print("❌ Signal rejected by AI Brain.")
        return jsonify({"status": "rejected by AI"}), 200

    # === STEP 3: Extract + Sanitize Data ===
    symbol = data.get("symbol", "Unknown")
    signal_type = data.get("type", "Unknown").upper()
    confidence = data.get("confidence", "0%")
    price = data.get("price", "N/A")
    tp = data.get("TP", "0.8%")
    sl = data.get("SL", "0.5%")

    # === Format Timestamp ===
    raw_timestamp = data.get("timestamp")
    try:
        dt = datetime.fromisoformat(raw_timestamp) if raw_timestamp else datetime.utcnow()
    except:
        dt = datetime.utcnow()
    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S UTC")

    # === STEP 4: Send to Telegram ===
    message = f"""
📉 *New Signal From Nova AI*

• *Symbol*: `{symbol}`
• *Type*: *{signal_type}*
• *Confidence*: *{confidence}*
• *Entry Price*: `${price}`
• *TP*: `{tp}` | *SL*: `{sl}`
• *Time*: `{timestamp}`

🧠 _Signal approved by AI Core_
"""
    send_telegram_message(message)

    # === STEP 5: Log It ===
    save_trade_to_log({
        "symbol": symbol,
        "type": signal_type,
        "confidence": confidence,
        "price": price,
        "tp": tp,
        "sl": sl,
        "timestamp": timestamp
    })

    return jsonify({"status": "forwarded by AI"}), 200

# === SEND TO TELEGRAM ===
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
        print("❌ Telegram error:", e)

# === LOG SIGNAL ===
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
