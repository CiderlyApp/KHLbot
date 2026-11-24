"""Normalized match representation used across the application."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Match:
    id: str
    start_at: datetime
    home: str
    away: str
    home_score: int | None = None
    away_score: int | None = None
    status: str = "Запланирован"
    arena: str | None = None

    @property
    def is_finished(self) -> bool:
        return self.home_score is not None and self.away_score is not None
