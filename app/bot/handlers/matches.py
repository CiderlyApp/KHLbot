"""Match list commands and callbacks."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.bot.utils import match_window
from app.formatting import format_matches

router = Router()

async def show_matches(target, service, timezone_name: str, kind: str):
    start, end = match_window(kind, timezone_name)
    matches = await service.in_range(start, end)
    heading = {"today": "Матчи сегодня", "tomorrow": "Матчи завтра", "week": "Ближайшие 7 дней"}[kind]
    text = format_matches(matches, heading)
    if len(text) > 4000:
        text = text[:3900] + "\n\n…Список сокращён."
    await target.answer(text)

@router.message(Command("today", "matches"))
async def today(message: Message, matches, timezone_name):
    await show_matches(message, matches, timezone_name, "today")

@router.message(Command("tomorrow"))
async def tomorrow(message: Message, matches, timezone_name):
    await show_matches(message, matches, timezone_name, "tomorrow")

@router.message(Command("week"))
async def week(message: Message, matches, timezone_name):
    await show_matches(message, matches, timezone_name, "week")

@router.callback_query(F.data.startswith("matches:"))
async def matches_callback(callback: CallbackQuery, matches, timezone_name):
    kind = callback.data.split(":", 1)[1]
    if kind not in {"today", "tomorrow", "week"}:
        await callback.answer("Неизвестный период", show_alert=True)
        return
    start, end = match_window(kind, timezone_name)
    items = await matches.in_range(start, end)
    heading = {"today": "Матчи сегодня", "tomorrow": "Матчи завтра", "week": "Ближайшие 7 дней"}[kind]
    await callback.message.answer(format_matches(items, heading))
    await callback.answer()
