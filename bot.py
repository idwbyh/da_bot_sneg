import os
import re
import threading
import telebot
from flask import Flask
import requests
import time
import gc

# === Telegram bot setup ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

YES_PATTERN = re.compile(r'^(да+|дa+|da+|dа+)$', re.IGNORECASE)

@bot.message_handler(func=lambda message: message.text and YES_PATTERN.match(message.text.strip()))
def reply_yes(message):
    bot.send_message(message.chat.id, "Пизда!")


@bot.message_handler(func=lambda message: True)
def ignore_all(message):
    pass

# === Flask web server ===
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!", 200

# === Функция для регулярного пинга самого себя ===
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
        time.sleep(600)  # 10 минут

# === Очистка кэша и сборка мусора каждые 5 минут ===
def cleanup_memory():
    while True:
        gc.collect()
        print("🧹 Очистка кэша и сборка мусора выполнена")
        time.sleep(300)  # 5 минут

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    print("✅ Бот запущен и слушает сообщения...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Flask веб-сервер в отдельном потоке
    threading.Thread(target=run_flask).start()
    # Пинг самого себя
    threading.Thread(target=self_ping).start()
    # Очистка кэша
    threading.Thread(target=cleanup_memory).start()
    # Бот
    run_bot()
