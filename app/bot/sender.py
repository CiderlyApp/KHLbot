"""Safe Telegram message sending helpers."""
import logging
from aiogram import Bot

logger = logging.getLogger(__name__)

async def send_text(bot: Bot, chat_id: int, text: str, **kwargs):
    try:
        return await bot.send_message(chat_id, text, **kwargs)
    except Exception:
        logger.exception("Telegram send failed for chat %s", chat_id)
        return None
