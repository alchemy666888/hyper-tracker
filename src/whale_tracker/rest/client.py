from datetime import datetime

import aiohttp

from whale_tracker.rest.rate_limiter import RateLimiter


class HyperliquidRESTClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.rate_limiter = RateLimiter()

    async def _post(self, path: str, payload: dict):
        await self.rate_limiter.wait()
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}{path}", json=payload) as response:
                response.raise_for_status()
                return await response.json()

    async def get_user_fills(self, wallet: str, since: datetime | None = None) -> list[dict]:
        payload = {"type": "userFills", "user": wallet}
        if since:
            payload["startTime"] = int(since.timestamp() * 1000)
        return await self._post("/info", payload)

    async def get_user_state(self, wallet: str) -> dict:
        return await self._post("/info", {"type": "clearinghouseState", "user": wallet})

    async def get_funding_history(self, market: str, limit: int = 1000) -> list[dict]:
        return await self._post("/info", {"type": "fundingHistory", "coin": market, "limit": limit})
