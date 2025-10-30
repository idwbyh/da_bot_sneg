import os
import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# TOKEN берем из переменных окружения (более безопасно)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set in environment")

# Endpoint для отправки сообщений
API_SEND = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Безопасный webhook-путь — используем токен в пути
WEBHOOK_PATH = f"/{TOKEN}"

# Нормализация и проверка варианта "да"
def is_da_variant(text: str) -> bool:
    if not text:
        return False
    t = "".join(ch for ch in text.lower() if ch.isalpha())
    # простая проверка: "да" или "da" или похожие транслит-варианты
    return t in ("да", "da")

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"ok": True})
    msg = data.get("message") or data.get("channel_post") or {}
    text = msg.get("text", "")
    chat = msg.get("chat", {})
    if chat and is_da_variant(text):
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
