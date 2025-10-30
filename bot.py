import os
import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Text

# -------------------------------------------------
# Конфигурация
# -------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не задана!")

# Список всех вариантов «да» (в нижнем регистре)
TRIGGERS = ["да", "da"]

# Регулярка – ищет любое слово из списка, игнорируя регистр
TRIGGER_REGEX = re.compile(r"\b(" + "|".join(re.escape(t) for t in TRIGGERS) + r")\b", re.IGNORECASE)

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

@dp.message(Text(TRIGGERS, ignore_case=True))
async def on_da(message: types.Message):
    """Ответ только в группах/супергруппах."""
    if message.chat.type in ("group", "supergroup"):
        await message.reply("Пизда")

# -------------------------------------------------
# Keep-alive (пинг каждые 4 минуты)
# -------------------------------------------------
KEEPALIVE_URL = os.getenv("RENDER_URL")  # Render автоматически задаёт переменную YOUR_SERVICE.onrender.com

async def keep_alive():
    """Периодический GET-запрос к самому сервису, чтобы Render не усыплял."""
    if not KEEPALIVE_URL:
        log.warning("RENDER_URL не задан – keep-alive отключён")
        return

    import aiohttp
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(KEEPALIVE_URL) as resp:
                    log.info(f"Keep-alive ping → {resp.status}")
            except Exception as e:
                log.error(f"Keep-alive error: {e}")
            await asyncio.sleep(240)  # 4 минуты

# -------------------------------------------------
# Очистка кэша (каждые 30 минут)
# -------------------------------------------------
CACHE_DIRS = [
    "/tmp",                     # Render использует /tmp как временное хранилище
    "/app/__pycache__",         # если вдруг появляется
]

async def clear_cache():
    """Удаляем всё, что старше 5 минут в указанных папках."""
    import shutil
    from pathlib import Path

    while True:
        for base in CACHE_DIRS:
            path = Path(base)
            if not path.exists():
                continue
            for item in path.iterdir():
                try:
                    # файлы и папки старше 5 минут
                    if item.stat().st_mtime < asyncio.get_event_loop().time() - 300:
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)
                except Exception as e:
                    log.debug(f"Cache clean skip {item}: {e}")
        await asyncio.sleep(1800)  # 30 минут

# -------------------------------------------------
# Запуск
# -------------------------------------------------
async def main():
    # Запускаем фоновые задачи
    asyncio.create_task(keep_alive())
    asyncio.create_task(clear_cache())

    log.info("Бот стартует…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())