import os
import asyncio
import logging
import re
import shutil
from pathlib import Path
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web, ClientSession

# ========================================
# КОНФИГ
# ========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не задан!")

PORT = int(os.getenv("PORT", 10000))
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

TRIGGERS = ["да", "da"]
TRIGGER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in TRIGGERS) + r")\b",
    re.IGNORECASE
)

logging.basicConfig