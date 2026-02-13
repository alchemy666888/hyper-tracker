from whale_tracker.positions.models import PositionState
from whale_tracker.whales.strategies import WhaleDetectionStrategy


class ThresholdStrategy(WhaleDetectionStrategy):
    def __init__(self, notional_threshold_usd: float = 100_000, volume_24h_threshold_usd: float = 1_000_000):
        self.notional_threshold = notional_threshold_usd
        self.volume_24h_threshold = volume_24h_threshold_usd

    async def get_market_volume_24h(self, market: str) -> float:
        _ = market
        return 0.0

    async def classify(self, position: PositionState) -> bool:
        notional = abs(float(position.size * position.entry_price))
        volume_24h = await self.get_market_volume_24h(position.market)
        return notional > self.notional_threshold or volume_24h > self.volume_24h_threshold

    async def get_confidence(self, position: PositionState) -> float:
        notional = abs(float(position.size * position.entry_price))
        return min(notional / max(self.notional_threshold, 1), 1.0)
