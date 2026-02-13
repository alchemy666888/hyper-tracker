import asyncio
import time


class RateLimiter:
    def __init__(self, requests_per_second: float = 10.0):
        self.interval = 1 / requests_per_second
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self._last_call = time.monotonic()
