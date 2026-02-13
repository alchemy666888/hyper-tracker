from datetime import datetime, timezone


class WhaleRegistry:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def add_whale(self, wallet: str, reason: str) -> None:
        await self.redis.sadd("whales:registry", wallet)
        await self.redis.hset(
            f"whale:metadata:{wallet}",
            mapping={"reason": reason, "added_at": datetime.now(timezone.utc).isoformat(), "last_active": datetime.now(timezone.utc).isoformat()},
        )

    async def is_whale(self, wallet: str) -> bool:
        return bool(await self.redis.sismember("whales:registry", wallet))

    async def auto_update_top_wallets(self) -> None:
        return None
