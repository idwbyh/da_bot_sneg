import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# TOKEN берем из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set in environment")

# Endpoint для отправки сообщений
API_SEND = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Безопасный webhook-путь — используем токен в пути
WEBHOOK_PATH = f"/{TOKEN}"


# Проверка: последнее слово "да" (игнорируем регистр и пробелы)
def ends_with_da(text: str) -> bool:
    if not text:
        return False
    words = text.strip().lower().split()
    return words[-1] == "да"


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"ok": True})

    msg = data.get("message") or data.get("channel_post") or {}
    text = msg.get("text", "")
    chat = msg.get("chat", {})

    if chat and ends_with_da(text):
        try:
            requests.post(API_SEND, json={
                "chat_id": chat["id"],
                "text": "пизда",
                "reply_to_message_id": msg.get("message_id")
            }, timeout=5)
        except Exception:
            pass

    return jsonify({"ok": True})


@app.route("/health", methods=["GET"])
def health():
    return "OK", 200


@app.route("/", methods=["GET"])
def index():
    return "Бот жив. Webhook path: " + WEBHOOK_PATH, 200
