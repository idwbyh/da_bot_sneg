import os
import asyncio
import logging
import re
import shutil
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# ========================================
# КОНФИГ
# ========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан!")

PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

TRIGGERS = ["да", "da"]
TRIGGER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in TRIGGERS) + r")\b",
    re.IGNORECASE
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ========================================
# БОТ
# ========================================
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message()
async def on_message(message: types.Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if TRIGGER_PATTERN.search(message.text or ""):
        try:
            await message.reply("Пизда")
        except Exception as e:
            log.error(f"Send error: {e}")

# ========================================
# KEEP-ALIVE
# ========================================
async def keep_alive():
    if not RENDER_URL:
        log.warning("No RENDER_EXTERNAL_URL – keep-alive disabled")
        return
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as r:
                    log.info(f"Ping: {r.status}")
            except Exception as e:
                log.error(f"Ping failed: {e}")
            await asyncio.sleep(240)

# ========================================
# ОЧИСТКА КЭША
# ========================================
async def clean_cache():
    paths = ["/tmp", "/app/__pycache__"]
    while True:
        for p in paths:
            path = Path(p)
            if not path.exists():
                continue
            for item in path.iterdir():
                try:
                    age = asyncio.get_event_loop().time() - item.stat().st_mtime
                    if age > 300:
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)
                except:
                    pass
        await asyncio.sleep(1800)

# ========================================
# ВЕБ-СЕРВЕР
# ========================================
async def health(request):
    return web.Response(text="OK")

app = web.Application()
app.router.add_get("/", health)

# ========================================
# ЗАПУСК
# ========================================
async def main():
    # Фоновые задачи
    asyncio.create_task(keep_alive())
    asyncio.create_task(clean_cache())

    # Веб-сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info(f"Web server on 0.0.0.0:{PORT}")

    # Бот
    log.info("Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())