import os
import re
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN") or "сюда_временно_вставь_твой_токен_из_BotFather"
bot = telebot.TeleBot(BOT_TOKEN)

YES_PATTERN = re.compile(r'^(да+|дa+|da+|dа+)$', re.IGNORECASE)

@bot.message_handler(func=lambda message: message.text and YES_PATTERN.match(message.text.strip()))
def reply_yes(message):
    bot.reply_to(message, "Согласен!")

@bot.message_handler(func=lambda message: True)
def ignore_all(message):
    pass

if __name__ == "__main__":
    print("✅ Бот запущен и слушает сообщения...")
    bot.infinity_polling()
