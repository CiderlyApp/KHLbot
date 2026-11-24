"""Upcoming-match notifications with persistent deduplication."""
import logging
from datetime import datetime, timedelta
from app.db.repositories import get_subscribers, was_notification_sent, mark_notification_sent
from app.formatting import format_match

logger = logging.getLogger(__name__)


async def send_upcoming_notifications(bot, matches, now: datetime, window_minutes: int = 30) -> int:
    sent = 0
    subscribers = get_subscribers()
    for user in subscribers:
        for match in matches:
            delta = (match.start_at - now).total_seconds()
            if not (0 <= delta <= window_minutes * 60):
                continue
            if user.favorite_team and user.favorite_team.casefold() not in (match.home + " " + match.away).casefold():
                continue
            if was_notification_sent(user.telegram_id, match.id):
                continue
            try:
                await bot.send_message(user.chat_id, "⏰ <bМатч скоро начнётся!</b>\n\n" + format_match(match))
                mark_notification_sent(user.telegram_id, match.id)
                sent += 1
            except Exception:
                logger.exception("Could not notify user %s", user.telegram_id)
    return sent
