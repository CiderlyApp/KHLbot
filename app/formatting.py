"""Russian-language formatting for match cards."""
from datetime import date
from .infrastructure.schemas import Match


def format_match(match: Match) -> str:
    time_text = match.start_at.strftime("%d.%m %H:%M")
    if match.is_finished:
        score = f"{match.home_score}:{match.away_score}"
        result = f"<b>{match.home}</b>  <b>{score}</b>  <b>{match.away}</b>"
    else:
        result = f"<b>{match.home}</b>  —  <b>{match.away}</b>"
    lines = [f"🏒 {result}", f"🕒 {time_text} · {match.status}"]
    if match.arena:
        lines.append(f"📍 {match.arena}")
    return "\n".join(lines)


def format_matches(matches: list[Match], heading: str) -> str:
    if not matches:
        return f"🏒 <b>{heading}</b>\n\nМатчей не найдено. Попробуй посмотреть ближайшие дни командой /week."
    return f"🏒 <b>{heading}</b>\n\n" + "\n\n".join(format_match(match) for match in matches[:20])
