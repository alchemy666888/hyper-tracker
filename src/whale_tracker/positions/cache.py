import json

from whale_tracker.positions.models import PositionDirection, PositionState


class PositionCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    def _key(self, wallet: str, market: str) -> str:
        return f"position:{wallet}:{market}"

    async def get_position(self, wallet: str, market: str) -> PositionState | None:
        raw = await self.redis.get(self._key(wallet, market))
        if not raw:
            return None
        data = json.loads(raw)
        data["direction"] = PositionDirection(data["direction"])
        return PositionState(**data)

    async def set_position(self, position: PositionState) -> None:
        payload = {
            **position.__dict__,
            "direction": position.direction.value,
            "entry_timestamp": position.entry_timestamp.isoformat(),
            "size": str(position.size),
            "entry_price": str(position.entry_price),
            "accumulated_funding": str(position.accumulated_funding),
            "realized_pnl": str(position.realized_pnl),
            "unrealized_pnl": str(position.unrealized_pnl),
        }
        await self.redis.set(self._key(position.wallet, position.market), json.dumps(payload), ex=86400)
        await self.redis.sadd(f"wallet_positions:{position.wallet}", position.market)

    async def invalidate(self, wallet: str, market: str) -> None:
        await self.redis.delete(self._key(wallet, market))
