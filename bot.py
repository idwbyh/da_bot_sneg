import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Токен из Render-переменных
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set in environment")

API_SEND = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
WEBHOOK_PATH = f"/{TOKEN}"

# Загружаем словарь реакций
with open("replies.json", "r", encoding="utf-8") as f:
    REPLIES = json.load(f)


def get_reply_for(text: str) -> str | None:
    if not text:
        return None
    t = text.lower().strip()
    for key, reply in REPLIES.items():
        if t.endswith(key):  # проверяем, оканчивается ли сообщение на ключ
            return reply
    return None


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"ok": True})
    msg = data.get("message") or {}
    text = msg.get("text", "")
    chat = msg.get("chat", {})

    reply = get_reply_for(text)
    if chat and reply:
        try:
            requests.post(API_SEND, json={
                "chat_id": chat["id"],
                "text": reply,
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
