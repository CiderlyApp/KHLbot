"""Optional local schedule fallback; used only when explicitly configured."""
import json
import logging
from pathlib import Path
from .khl_api import parse_matches

logger = logging.getLogger(__name__)


def load_fallback(path: str = "data/fallback_schedule.json", timezone_name: str = "Europe/Moscow"):
    file = Path(path)
    if not file.exists():
        return []
    try:
        return parse_matches(json.loads(file.read_text(encoding="utf-8")), timezone_name)
    except (OSError, ValueError) as exc:
        logger.warning("Could not load fallback schedule: %s", exc)
        return []
