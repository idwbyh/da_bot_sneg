import os
import json
import requests
from flask import Flask, request, jsonify

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # обязательно
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # например https://your-service.onrender.com/webhook
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = Flask(__name__)

# ---- простая нормализация: убираем пробелы/пунктуацию, приводим к lower ----
def normalize(text: str) -> str:
    if not text:
        return ""
    txt = text.strip().lower()
    # оставить только буквы (кириллица + латиница)
    txt = "".join(ch for ch in txt if ch.isalpha())
    return txt

# ---- простая конверсия cyrillic->latin для пары букв, и latin->cyrillic ----
# (достаточно для "да" <-> "da" обработки)
CYR_TO_LAT = {"д": "d", "а": "a"}
LAT_TO_CYR = {"d": "д", "a": "а"}

def cyr_to_lat(s: str) -> str:
    return "".join(CYR_TO_LAT.get(ch, ch) for ch in s)

def lat_to_cyr(s: str) -> str:
    return "".join(LAT_TO_CYR.get(ch, ch) for ch in s)

def is_da_variant(text: str) -> bool:
    """
    Возвращает True если нормализованный текст — это "да" (кириллица) или "da" (латиница)
    с учётом возможного смешения букв.
    """
    n = normalize(text)
    if not n:
        return False
    if n == "да" or n == "da":
        return True
    # попробовать преобразовать: кир->лат и лат->кир
    if cyr_to_lat(n) == "da":
        return True
    if lat_to_cyr(n) == "да":
        return True
    return False

def send_message(chat_id: int, text: str, reply_to_message_id: int = None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id
    requests.post(f"{API_URL}/sendMessage", json=payload, timeout=10)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Telegram присылает JSON с апдейтом
    update = request.get_json(force=True)
    # безопасность: не логируем всё, избегаем роста логов
    msg = update.get("message") or update.get("channel_post") or {}
    if not msg:
        return jsonify({"ok": True})

    chat = msg.get("chat", {})
    chat_type = chat.get("type", "")
    text = msg.get("text", "")
    # реагируем только в группах/супергруппах
    if chat_type in ("group", "supergroup"):
        if is_da_variant(text):
            # отправляем ответ в тот же чат.
            # можно отвечать в реплай, но по задаче просто отправляем "пизда"
            # отвечаем реплай-ответом, чтобы было видно связь
            send_message(chat["id"], "пизда", reply_to_message_id=msg.get("message_id"))
    return jsonify({"ok": True})

@app.route("/health", methods=["GET"])
def health():
    # простой эндпоинт для пинга (UptimeRobot / Render cron)
    return "OK", 200

def set_webhook():
    """Если задан WEBHOOK_URL — пытаемся зарегистрировать вебхук у Telegram."""
    if not WEBHOOK_URL:
        print("WEBHOOK_URL не задан, пропускаю setWebhook.")
        return
    try:
        resp = requests.post(f"{API_URL}/setWebhook", json={"url": WEBHOOK_URL}, timeout=10)
        print("setWebhook:", resp.status_code, resp.text)
    except Exception as e:
        print("Ошибка setWebhook:", e)

if __name__ == "__main__":
    # при запуске локально (debug) попытка зарегистрировать вебхук — опционально
    set_webhook()
    # Для Render/production — запускайте через gunicorn: gunicorn main:app --bind 0.0.0.0:$PORT
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
