from datetime import datetime
from zoneinfo import ZoneInfo
from app.formatting import format_match, format_matches
from app.infrastructure.schemas import Match


def test_format_upcoming_match_contains_teams_and_time():
    match = Match("1", datetime(2026, 11, 24, 19, 30, tzinfo=ZoneInfo("Europe/Moscow")), "СКА", "ЦСКА")
    result = format_match(match)
    assert "СКА" in result and "ЦСКА" in result and "19:30" in result


def test_empty_match_list_has_actionable_hint():
    assert "/week" in format_matches([], "Матчи сегодня")
