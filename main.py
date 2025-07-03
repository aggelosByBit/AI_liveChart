from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# === TELEGRAM BOT SETTINGS ===
BOT_TOKEN = "7832911275:AAGqXqBScHOOMyBf8yxSmJmPxenzEBhpFNo"
CHAT_ID = "-1002526774762"

# === ROOT ENDPOINT TO AVOID 404 ON RENDER ===
@app.route('/')
def index():
    return "✅ Nova AI Webhook is running."

# === ROUTE TO RECEIVE SIGNAL FROM TRADINGVIEW ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON payload received'}), 400

    message = f"📈 Signal Received:\n\n{data}"
    send_telegram_message(message)
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
        return response.json()
    except Exception as e:
        print("Telegram error:", e)

# === PORT BINDING FOR RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
