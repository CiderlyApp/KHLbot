"""Schedule synchronization helpers shared by diagnostics and notification jobs."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.services.matches import MatchService


async def sync_upcoming_matches(
    service: MatchService,
    timezone_name: str = "Europe/Moscow",
    days: int = 7,
):
    """Fetch and return matches in the requested upcoming time window."""
    timezone = ZoneInfo(timezone_name)
    now = datetime.now(timezone)
    end = now + timedelta(days=days)
    return await service.in_range(now, end)
