from whale_tracker.positions.models import PositionState
from whale_tracker.whales.strategies import WhaleDetectionStrategy


class HybridWhaleDetector:
    def __init__(self, strategies: list[WhaleDetectionStrategy], require_all: bool = False):
        self.strategies = strategies
        self.require_all = require_all

    async def is_whale(self, position: PositionState) -> bool:
        if self.require_all:
            results = [await strategy.classify(position) for strategy in self.strategies]
            return all(results)
        results = [await strategy.classify(position) for strategy in self.strategies]
        return any(results)

    async def get_whale_score(self, position: PositionState) -> float:
        scores = [await strategy.get_confidence(position) for strategy in self.strategies]
        return sum(scores) / len(scores) if scores else 0.0
