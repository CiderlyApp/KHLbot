"""Inline keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Матчи сегодня", callback_data="matches:today"), InlineKeyboardButton(text="Завтра", callback_data="matches:tomorrow")],
        [InlineKeyboardButton(text="На неделю", callback_data="matches:week")],
        [InlineKeyboardButton(text="Уведомления: включить", callback_data="notifications:on"), InlineKeyboardButton(text="Выбрать команду", callback_data="team:choose")],
    ])


def teams_keyboard(teams: list[str]):
    rows = [[InlineKeyboardButton(text=team, callback_data=f"team:set:{team}")] for team in teams]
    rows.append([InlineKeyboardButton(text="Все команды", callback_data="team:set:all")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
