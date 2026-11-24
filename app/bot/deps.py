"""Shared application dependencies."""
from dataclasses import dataclass
from aiogram import Bot
from app.services.matches import MatchService

@dataclass
class BotContext:
    bot: Bot
    matches: MatchService
    timezone_name: str
