from flask import Flask, request
import requests
import threading
import time
import re

app = Flask(__name__)

TOKEN = "8311688244:AAHl_uEV5ZBrDG4aTK9EhzyM_B2kyiKE2ZU"
URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
PING_URL = "https://da-bot-sneg.onrender.com"  # твой Render-домен

# --- Ответ бота ---
def check_message(text: str) -> bool:
    text = text.lower().replace(" ", "")
    return bool(re.search(r"^(da|да|d+a+)$", text))

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok"

    message = data["message"]
    text = message.get("text", "")
    chat_id = message["chat"]["id"]

    if check_message(text):
        requests.post(URL, json={
            "chat_id": chat_id,
            "text": "пизда"
        })

    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Бот жив"

# --- Поддержка живого состояния Render ---
def keep_alive():
    while True:
        try:
            requests.get(PING_URL)
        except Exception:
            pass
        time.sleep(300)  # каждые 5 минут пинг

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
