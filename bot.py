import os
import re
import threading
import requests
import gc
import time
from flask import Flask, request
import telebot

# === Настройка бота ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Все варианты "да" (регистр, транслит)
YES_PATTERN = re.compile(r'^(да+|дa+|da+|dа+)$', re.IGNORECASE)

@bot.message_handler(func=lambda message: message.text and YES_PATTERN.match(message.text.strip()))
def reply_yes(message):
    bot.send_message(message.chat.id, "пизда!")

# Игнорируем все остальные сообщения
@bot.message_handler(func=lambda message: True)
def ignore_all(message):
    pass

# === Flask сервер для Render ===
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!", 200

@app.route("/" + BOT_TOKEN, methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# === Функция для самопинга ===
def self_ping():
    url = os.environ.get("SELF_URL")
    if not url:
        print("⚠️ SELF_URL не установлен — пингование не будет работать")
        return
    while True:
        try:
            requests.get(url, timeout=5)
            print("🔄 Self-ping выполнен")
        except Exception as e:
            print(f"❌ Ошибка пинга: {e}")
        time.sleep(600)  # каждые 10 минут

# === Очистка кэша и сборка мусора каждые 5 минут ===
def cleanup_memory():
    while True:
        gc.collect()
        print("🧹 Очистка кэша выполнена")
        time.sleep(300)

if __name__ == "__main__":
    # Убираем старый webhook и ставим новый
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get("SELF_URL") + BOT_TOKEN)

    # Пинг и очистка кэша в отдельном потоке
    threading.Thread(target=self_ping, daemon=True).start()
    threading.Thread(target=cleanup_memory, daemon=True).start()

    # Запуск Flask
    port = int(os.environ.get("PORT", 8080))
    print("✅ Бот запущен через webhook, ждём сообщения Telegram...")
    app.run(host="0.0.0.0", port=port)
