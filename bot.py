import os
import asyncio
import logging
import re
import shutil
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# ========================================
# НАСТРОЙКИ
# ========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в переменных окружения!")

PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render даёт автоматически

# Варианты "да"
TRIGGERS = ["да", "da"]
TRIGGER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in TRIGGERS) + r")\b",
    re.IGNORECASE
)

# Логи
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ========================================
# БОТ
# ========================================
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    # Только группы
    if message.chat.type not in ("group", "supergroup"):
        return

    text = message.text or ""
    if TRIGGER_PATTERN.search(text):
        try:
            await message.reply("Пизда")
        except Exception as e:
            log.error(f"Ошибка отправки: {e}")

# ========================================
# KEEP-ALIVE (чтобы Render не усыплял)
# ========================================
async def keep_alive():
    if not RENDER_URL:
        log.warning("RENDER_EXTERNAL_URL не найден – keep-alive отключён")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as resp:
                    log.info(f"Keep-alive ping: {resp.status}")
            except Exception as e:
                log.error(f"Keep-alive error: {e}")
            await asyncio.sleep(240)  # каждые 4 минуты

# ========================================
# ОЧИСТКА КЭША (чтобы не забить 500 МБ)
# ========================================
async def clear_cache():
    paths_to_clean = ["/tmp", "/app/__pycache__"]
    while True:
        for p in paths_to_clean:
            path = Path(p)
            if not path.exists():
                continue
            for item in path.iterdir():
                try:
                    age = asyncio.get_event_loop().time() - item.stat().st_mtime
                    if age > 300:  # старше 5 минут