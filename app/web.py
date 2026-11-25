
"""FastAPI webhook entry point for Render Free Web Service."""

import hmac
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import get_settings
from app.db.base import configure_database
from app.logging_setup import configure_logging
from app.services.matches import MatchService
from app.bot.handlers import (
    common_router,
    matches_router,
    preferences_router,
    fallback_router,
)
from app.scheduler import run_notification_job


settings = get_settings()

configure_logging(settings.log_level)

logger = logging.getLogger(__name__)

# Initialize Telegram bot with HTML message formatting.
bot = Bot(
    token=settings.bot_token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)

dp = Dispatcher()

dp.include_routers(
    common_router,
    matches_router,
    preferences_router,
    fallback_router,
)

match_service = MatchService(
    settings.season,
    settings.timezone,
)

dp.workflow_data.update(
    matches=match_service,
    timezone_name=settings.timezone,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources and configure Telegram webhook."""

    configure_database(settings.database_url)

    webhook_base_url = (
        settings.webhook_url
        or os.getenv("RENDER_EXTERNAL_URL")
    )

    if webhook_base_url:
        if not settings.webhook_secret:
            raise RuntimeError(
                "WEBHOOK_SECRET is required when webhook URL is configured"
            )

        await bot.set_webhook(
            url=webhook_base_url.rstrip("/") + settings.webhook_path,
            secret_token=settings.webhook_secret,
            drop_pending_updates=True,
            allowed_updates=dp.resolve_used_update_types(),
        )

        logger.info("Telegram webhook configured")

    yield

    await bot.session.close()


app = FastAPI(
    title="KHLbot",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Return basic service information."""

    return {
        "service": "KHLbot",
        "status": "ok",
    }


@app.get("/health")
async def health():
    """Health check endpoint for Render."""

    return {"status": "ok"}


@app.post(
    settings.webhook_path
    if settings.webhook_secret
    else "/telegram/webhook"
)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    """Receive and process Telegram webhook updates."""

    if settings.webhook_secret and not hmac.compare_digest(
        x_telegram_bot_api_secret_token or "",
        settings.webhook_secret,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid webhook secret",
        )

    payload = await request.json()

    update = Update.model_validate(
        payload,
        context={"bot": bot},
    )

    await dp.feed_update(bot, update)

    return {"ok": True}


@app.post("/jobs/notify")
async def notify_job(
    x_job_token: str | None = Header(default=None),
):
    """Run scheduled match notifications."""

    if not settings.job_token or not hmac.compare_digest(
        x_job_token or "",
        settings.job_token,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid job token",
        )

    count = await run_notification_job(
        bot,
        match_service,
        settings.timezone,
    )

    return {
        "status": "ok",
        "notifications_sent": count,
    }
