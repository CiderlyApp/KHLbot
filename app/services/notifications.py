"""Upcoming-match notifications with persistent deduplication."""
import logging
from datetime import datetime
from app.db.repositories import get_subscribers, was_notification_sent, mark_notification_sent
from app.formatting import format_match

logger = logging.getLogger(__name__)

# Header is HTML, so parse_mode="HTML" must be passed to send_message.
# Fixed: the opening tag was "<bМатч" (missing ">").
NOTIFICATION_HEADER = "⏰ <b>Матч скоро начнётся!</b>\n\n"


async def send_upcoming_notifications(bot, matches, now: datetime, window_minutes: int = 30) -> int:
    """Notify subscribers about matches starting within `window_minutes`.

    Skips matches outside the window, matches not involving the user's
    favorite team (if set), and notifications already sent (persistent dedup).

    Returns the number of notifications successfully sent.
    """
    sent = 0
    subscribers = get_subscribers()
    for user in subscribers:
        for match in matches:
            # Only matches starting within the next `window_minutes`
            delta = (match.start_at - now).total_seconds()
            if not (0 <= delta <= window_minutes * 60):
                continue

            # Favorite-team filter (case-insensitive substring match)
            if user.favorite_team and user.favorite_team.casefold() not in (
                match.home + " " + match.away
            ).casefold():
                continue

            # Persistent deduplication across restarts
            if was_notification_sent(user.telegram_id, match.id):
                continue

            try:
                await bot.send_message(
                    user.chat_id,
                    NOTIFICATION_HEADER + format_match(match),
                    parse_mode="HTML",  # without this, tags are shown literally
                )
                mark_notification_sent(user.telegram_id, match.id)
                sent += 1
            except Exception:
                logger.exception("Could not notify user %s", user.telegram_id)
    return sent