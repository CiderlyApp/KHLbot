from datetime import datetime
from zoneinfo import ZoneInfo
from app.infrastructure.schemas import Match


def test_match_finished_only_when_both_scores_exist():
    start = datetime(2026, 11, 24, 19, 0, tzinfo=ZoneInfo("Europe/Moscow"))
    assert not Match("1", start, "СКА", "ЦСКА", 2, None).is_finished
    assert Match("2", start, "СКА", "ЦСКА", 2, 1).is_finished
