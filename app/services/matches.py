"""Match queries with a short in-process cache and API fallback behavior."""
import logging
import time
from app.infrastructure.khl_api import KHLApiClient
from app.infrastructure.fallback import load_fallback

logger = logging.getLogger(__name__)


class MatchService:
    def __init__(self, season: int, timezone_name: str, cache_ttl: int = 60):
        self.client = KHLApiClient(timezone_name)
        self.season = season
        self.timezone_name = timezone_name
        self.cache_ttl = cache_ttl
        self._cache = []
        self._cache_until = 0.0

    async def upcoming(self, days: int = 7):
        """Return a cached short schedule to avoid calling the provider per user."""
        if self._cache and time.monotonic() < self._cache_until:
            return self._cache
        try:
            matches = await self.client.get_matches(self.season)
            if matches:
                self._cache = matches
                self._cache_until = time.monotonic() + self.cache_ttl
                return matches
        except Exception:
            logger.exception("KHL API request failed")
        fallback = load_fallback(timezone_name=self.timezone_name)
        if fallback:
            self._cache = fallback
            self._cache_until = time.monotonic() + min(self.cache_ttl, 30)
        return fallback

    async def in_range(self, start, end):
        return [m for m in await self.upcoming() if start <= m.start_at < end]
