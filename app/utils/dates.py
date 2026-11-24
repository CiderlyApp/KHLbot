"""Date window helpers."""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


def day_window(day_offset: int, timezone_name: str):
    tz = ZoneInfo(timezone_name)
    today = datetime.now(tz).date() + timedelta(days=day_offset)
    return datetime.combine(today, time.min, tzinfo=tz), datetime.combine(today + timedelta(days=1), time.min, tzinfo=tz)
