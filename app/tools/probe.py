"""Simple external API probe used during local diagnostics."""
import asyncio
from app.infrastructure.khl_api import KHLApiClient

async def main():
    from app.config import get_settings
    settings = get_settings()
    matches = await KHLApiClient(settings.timezone).get_matches(settings.season)
    print(f"Loaded {len(matches)} KHL matches")
    for match in matches[:5]:
        print(match)

if __name__ == "__main__":
    asyncio.run(main())
