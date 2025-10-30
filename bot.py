import os
import asyncio
import logging
import re
import shutil
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, RegexpCommandsFilter
import aiohttp

# -------------------------------------------------
# Конфигурация
# -------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан!")

# Все варианты "да" (регистронезависимо)
TRIGGERS = ["да", "da"]
TRIGGER_REGEX = re.compile(r"\b(" + "|".join(re.escape(t) for t in TRIGGERS) + r")\b", re.IGNORECASE)

# Порт для веб-сервера (Render требует)
PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render даёт эту переменную автоматически

# -------------------------------------------------
# Логи
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# -------------------------------------------------
# Бот
# -------------------------------------------------
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message()
async def on_message(message: types.Message):
    """Ловим любое сообщение в группах"""
    if message.chat.type not in ("group", "supergroup"):
        return

    if TRIGGER_REGEX.search(message.text or ""):
        await message.reply("Пизда")

# -------------------------------------------------
# Keep-alive (пинг каждые 4 минуты)
# -------------------------------------------------
async def keep_alive():
    if not RENDER_URL:
        log.warning("RENDER_EXTERNAL_URL не найден – keep-alive отключён")
        return

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as resp:
                    log.info(f"Keep-alive → {resp.status}")
            except Exception as e:
                log.error(f"Keep-alive error: {e}")
            await asyncio.sleep(240)  # 4 минуты

# -------------------------------------------------
# Очистка кэша
# -------------------------------------------------
async def clear_cache():
    while True:
        for path_str in ["/tmp", "/app/__pycache__"]:
            path = Path(path_str)
            if not path.exists():
                continue
            for item in path.iterdir():
                try:
                    if item.stat().st_mtime < asyncio.get_event_loop().time() - 300:
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)
                except:
                    pass
        await asyncio.sleep(1800)  # 30 минут

# -------------------------------------------------
# Веб-сервер (обязателен для Render!)
# -------------------------------------------------
from aiohttp import web

async def health_check(request):
    return web.Response(text="OK")

app = web.Application()
app.router.add_get('/', health_check)

# -------------------------------------------------
# Запуск
# -------------------------------------------------
async def main():
    # Фоновые задачи
    asyncio.create_task(keep_alive())
    asyncio.create_task(clear_cache())

    # Запускаем веб-сервер и бота параллельно
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"Веб-сервер запущен на 0.0.0.0:{PORT}")

    log.info("Бот стартует (long-polling)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())