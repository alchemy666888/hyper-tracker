import asyncio

from whale_tracker.config import Settings
from whale_tracker.logging import logger


async def run() -> None:
    settings = Settings()
    logger.info("tracker_starting", ws_url=settings.ws_url)
    await asyncio.sleep(0)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
