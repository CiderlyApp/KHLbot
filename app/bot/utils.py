"""Helpers for bot handlers."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from app.utils.dates import day_window


def match_window(kind: str, timezone_name: str):
    if kind == "today":
        return day_window(0, timezone_name)
    if kind == "tomorrow":
        return day_window(1, timezone_name)
    tz = ZoneInfo(timezone_name)
    now = datetime.now(tz)
    return now, now + timedelta(days=7)
