"""Application settings loaded from environment variables."""
from functools import lru_cache
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    webhook_url: str | None = None
    webhook_secret: str | None = None
    job_token: str | None = None
    database_url: str = "sqlite:///./data/khlbot.db"
    timezone: str = "Europe/Moscow"
    khl_season: int | None = None
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def season(self) -> int:
        if self.khl_season:
            return self.khl_season
        now = datetime.now(ZoneInfo(self.timezone))
        return now.year + (1 if now.month >= 7 else 0)

    @property
    def webhook_path(self) -> str:
        secret = self.webhook_secret or ""
        return f"/telegram/{secret}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
