"""Run bot locally with long polling. Render should use the webhook app."""
import asyncio
from aiogram import Bot, Dispatcher
from app.config import get_settings
from app.db.base import configure_database
from app.logging_setup import configure_logging
from app.services.matches import MatchService
from app.bot.handlers import common_router, matches_router, preferences_router, fallback_router

async def main():
    settings = get_settings()
    configure_logging(settings.log_level)
    configure_database(settings.database_url)
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_routers(common_router, matches_router, preferences_router, fallback_router)
    dp.workflow_data.update(matches=MatchService(settings.season, settings.timezone), timezone_name=settings.timezone)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
