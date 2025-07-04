from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# === TELEGRAM BOT SETTINGS ===
BOT_TOKEN = "7832911275:AAGqXqBScHOOMyBf8yxSmJmPxenzEBhpFNo"
CHAT_ID = "-1002526774762"

# === DEFAULT TP/SL SETTINGS ===
DEFAULT_TP = "0.8%"
DEFAULT_SL = "0.5%"

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

    symbol = data.get("symbol", "Unknown")
    signal_type = data.get("type", "Unknown").upper()
    confidence = data.get("confidence", "0%")
    timestamp = data.get("timestamp", "Unknown")
    tp = data.get("TP", DEFAULT_TP)
    sl = data.get("SL", DEFAULT_SL)

    # Parse confidence as number
    try:
        confidence_value = float(confidence.replace('%', '').strip())
    except:
        confidence_value = 0

    if confidence_value >= 80:
        message = f"""
📊 *Nova Signal Alert*

• *Symbol*: `{symbol}`
• *Type*: *{signal_type}*
• *Confidence*: *{confidence}*
• *Time*: `{timestamp}`
• *TP*: `{tp}` | *SL*: `{sl}`

🧠 _Signal accepted by Nova Core (≥80% confidence)_
"""
        send_telegram_message(message)
    else:
        print("❌ Signal rejected (below confidence threshold)")

    return jsonify({'status': 'ok'}), 200

# === SEND TELEGRAM MESSAGE ===
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

# === PORT BINDING FOR RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
