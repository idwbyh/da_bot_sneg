import os
import re
import threading
import telebot
from flask import Flask

# === Telegram bot setup ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# шаблон, который ловит все варианты "да", "дa", "ДА", "da", "dA" и т.д.
YES_PATTERN = re.compile(r'^(да+|дa+|da+|dа+|Да+|Da+|ДА+|DA)$', re.IGNORECASE)

@bot.message_handler(func=lambda message: message.text and YES_PATTERN.match(message.text.strip()))
def reply_yes(message):
    bot.reply_to(message, "Согласен!")

@bot.message_handler(func=lambda message: True)
def ignore_all(message):
    pass

# === Flask web server (фиктивный) ===
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    print("✅ Бот запущен и слушает сообщения...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке, чтобы Render видел открытый порт
    threading.Thread(target=run_flask).start()
    # Запускаем бота
    run_bot()
