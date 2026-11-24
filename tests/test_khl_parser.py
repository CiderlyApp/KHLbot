from app.infrastructure.khl_api import parse_matches


def test_parse_webcaster_event_epoch_milliseconds():
    payload = {"events": [{"id": 123, "event_start_at": 1795543200000,
        "team_a": "СКА", "team_b": "ЦСКА", "score": "2:1"}]}
    matches = parse_matches(payload)
    assert len(matches) == 1
    assert matches[0].id == "123"
    assert matches[0].home == "СКА"
    assert matches[0].away == "ЦСКА"
    assert matches[0].home_score == 2
    assert matches[0].away_score == 1


def test_parser_skips_incomplete_rows():
    assert parse_matches({"events": [{"id": 1, "team_a": "СКА"}]}) == []
