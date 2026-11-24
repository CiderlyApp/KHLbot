"""Client for the public KHL Webcaster mobile JSON API."""
import logging
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import httpx
from .schemas import Match

logger = logging.getLogger(__name__)
BASE_URL = "https://khl.api.webcaster.pro/api/khl_mobile"


def _first(obj: dict, *keys, default=None):
    for key in keys:
        value = obj.get(key)
        if value not in (None, ""):
            return value
    return default


def _parse_start(item: dict, tz: ZoneInfo):
    raw = _first(item, "event_start_at", "start_at", "date_start", "date")
    if raw is None:
        return None
    try:
        if isinstance(raw, (int, float)) or str(raw).isdigit():
            value = float(raw)
            if value > 10_000_000_000:
                value /= 1000
            return datetime.fromtimestamp(value, timezone.utc).astimezone(tz)
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=tz) if parsed.tzinfo is None else parsed.astimezone(tz)
    except (ValueError, TypeError, OverflowError):
        return None


def _score(item: dict, side: str):
    direct = _first(item, f"score_{side}", f"{side}_score", f"team_{side}_score")
    if direct is not None:
        try:
            return int(direct)
        except (TypeError, ValueError):
            pass
    score = item.get("score")
    if isinstance(score, str) and ":" in score:
        try:
            return int(score.split(":")[0 if side in ("a", "home") else 1])
        except (ValueError, IndexError):
            pass
    return None


def parse_matches(payload, timezone_name: str = "Europe/Moscow") -> list[Match]:
    """Parse API envelopes defensively; unknown records are skipped, not fabricated."""
    tz = ZoneInfo(timezone_name)
    if isinstance(payload, dict):
        rows = _first(payload, "events", "data", "items", "results", default=[])
        if isinstance(rows, dict):
            rows = _first(rows, "events", "items", "data", default=[])
    else:
        rows = payload
    if not isinstance(rows, list):
        return []
    matches = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        start_at = _parse_start(item, tz)
        home = _first(item, "team_a", "home_team", "home_name", "team_a_name", "home")
        away = _first(item, "team_b", "away_team", "visitor_name", "team_b_name", "away")
        if isinstance(home, dict):
            home = _first(home, "name", "title", "full_name")
        if isinstance(away, dict):
            away = _first(away, "name", "title", "full_name")
        if not start_at or not home or not away:
            continue
        match_id = _first(item, "id", "event_id", "khl_id", "match_id")
        if match_id is None:
            match_id = f"{start_at.isoformat()}:{home}:{away}"
        status_value = _first(item, "status", "status_name", "game_state_key", "game_state")
        status = "Завершён" if status_value == "finished" else str(status_value or "Запланирован")
        arena = _first(item, "arena", "arena_name", "venue")
        matches.append(Match(
            id=str(match_id), start_at=start_at, home=str(home), away=str(away),
            home_score=_score(item, "a"), away_score=_score(item, "b"),
            status=status, arena=str(arena) if arena else None,
        ))
    return sorted(matches, key=lambda match: match.start_at)


class KHLApiClient:
    def __init__(self, timezone_name: str = "Europe/Moscow", timeout: float = 15.0):
        self.timezone_name = timezone_name
        self.timeout = timeout

    async def get_matches(self, season: int, stage: str = "regular", pages: int = 5) -> list[Match]:
        headers = {"User-Agent": "KHLbot/1.0 (+https://github.com/karapuz14/KHLbot)"}
        now = int(time.time())
        params = {
            "season": season,
            "stage": stage,
            "locale": "ru",
            "q[start_at_gt_time_from_unixtime]": now - 24 * 60 * 60,
            "q[start_at_lt_time_from_unixtime]": now + 8 * 24 * 60 * 60,
        }
        all_matches: dict[str, Match] = {}
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            for page in range(1, pages + 1):
                response = await client.get(f"{BASE_URL}/events_v2.json", params={**params, "page": page})
                response.raise_for_status()
                batch = parse_matches(response.json(), self.timezone_name)
                if not batch:
                    break
                for match in batch:
                    all_matches[match.id] = match
                if len(batch) < 16:
                    break
        return sorted(all_matches.values(), key=lambda match: match.start_at)
