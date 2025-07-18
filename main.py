from flask import Flask, request, jsonify
import requests
import os
import json
from datetime import datetime
from logger import log_signal

app = Flask(__name__)

# === TELEGRAM BOT SETTINGS ===
BOT_TOKEN = "7832911275:AAGqXqBScHOOMyBf8yxSmJmPxenzEBhpFNo"
CHAT_ID = "-1002526774762"

# === AI BRAIN SETTINGS ===
AI_BRAIN_URL = "https://novabrain.replit.app/webhook"
AI_TIMEOUT = 10  # ⬅ increased to give Replit more time

# === ROOT ENDPOINT ===
@app.route('/')
def index():
    return "✅ Nova AI Webhook (Render) is live."


# === MAIN WEBHOOK ENDPOINT ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON payload received'}), 400

    print("✅ Received Webhook Data:", data)

    # === STEP 1: Forward to AI Brain (with retry logic) ===
    try:
        ai_response = requests.post(AI_BRAIN_URL, json=data, timeout=AI_TIMEOUT)
        ai_json = ai_response.json()
        print("🧠 AI Response:", ai_json)
    except Exception as e:
        print("❌ Failed to reach AI Brain:", str(e))
        return jsonify({"error": "AI Brain unreachable"}), 502

    # === STEP 2: Check AI Decision ===
    if ai_json.get("final_decision") != "forwarded":
        print("❌ Signal rejected by AI Brain.")
        return jsonify({"status": "rejected by AI"}), 200

    # === STEP 3: Forward to Final Endpoint (/final) ===
    try:
        final_url = os.environ.get("FORWARD_URL")
        forward_response = requests.post(final_url, json=data, timeout=5)
        print("➡️ Forwarded to /final:", forward_response.status_code)
    except Exception as e:
        print("❌ Failed to forward to final:", str(e))
        return jsonify({"error": "Failed to forward"}), 502

    return jsonify({"status": "forwarded by AI"}), 200


# === FINAL FORWARD ENDPOINT (Telegram + log) ===
@app.route('/final', methods=['POST'])
def final_telegram_forward():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    # Extract info
    symbol = data.get("symbol", "Unknown")
    signal_type = data.get("type", "Unknown").upper()
    confidence = data.get("confidence", "N/A")
    price = data.get("price", "N/A")
    tp = data.get("TP", "N/A")
    sl = data.get("SL", "N/A")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())

    message = f"""
📉 *Nova AI Verified Signal*

• *Symbol*: `{symbol}`
• *Type*: *{signal_type}*
• *Confidence*: *{confidence}*
• *Entry Price*: `${price}`
• *TP*: `{tp}` | *SL*: `{sl}`
• *Time*: `{timestamp}`

✅ _Forwarded by AI Core_
"""

    send_telegram_message(message)
    save_trade_to_log(data)

    return jsonify({"status": "forwarded to Telegram"}), 200


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
        print("✅ Telegram response:", response.status_code)
        return response.json()
    except Exception as e:
        print("❌ Telegram send error:", str(e))


# === LOG LOCALLY ===
def save_trade_to_log(trade_data):
    try:
        log_signal({
            "timestamp": trade_data.get("timestamp"),
            "type": trade_data.get("type"),
            "symbol": trade_data.get("symbol"),
            "price": trade_data.get("price"),
            "confidence": trade_data.get("confidence"),
            "TP": trade_data.get("TP"),
            "SL": trade_data.get("SL"),
        })
        print("✅ Trade logged successfully.")
    except Exception as e:
        print("❌ Logging failed:", str(e))


# === BIND PORT FOR RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
