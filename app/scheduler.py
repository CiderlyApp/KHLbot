"""Notification job entry point; invoked by GitHub Actions on Render Free."""
from datetime import datetime
from zoneinfo import ZoneInfo
from app.services.notifications import send_upcoming_notifications

async def run_notification_job(bot, match_service, timezone_name: str) -> int:
    tz = ZoneInfo(timezone_name)
    now = datetime.now(tz)
    matches = await match_service.upcoming(2)
    return await send_upcoming_notifications(bot, matches, now)
