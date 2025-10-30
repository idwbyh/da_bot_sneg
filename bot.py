import os
import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiohttp import web
import aiohttp

# ========================================
# КОНФИГ
# ========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан!")

PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

TRIGGERS = ["да", "da"]
TRIGGER_PATTERN = re.compile(r"\b(" + "|".join(re.escape(t) for t in TRIGGERS) + r")\b", re.IGNORECASE)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ========================================
# БОТ
# ========================================
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message()
async def on_da(message: types.Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if TRIGGER_PATTERN.search(message.text or ""):
        await message.reply("Пизда")

# ========================================
# KEEP-ALIVE
# ========================================
async def keep_alive():
    if not RENDER_URL:
        return
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as r:
                    log.info(f"Ping: {r.status}")
            except:
                pass
            await asyncio.sleep(240)

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
    asyncio.create_task(keep_alive())

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    log.info("Web server OK")

    log.info("Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())