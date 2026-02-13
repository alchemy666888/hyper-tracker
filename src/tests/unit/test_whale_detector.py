import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from whale_tracker.positions.models import PositionDirection, PositionState
from whale_tracker.whales.detector import HybridWhaleDetector
from whale_tracker.whales.filters import ThresholdStrategy


def test_hybrid_detector_or_logic():
    async def run():
        position = PositionState(
            wallet="0xabc",
            market="BTC",
            direction=PositionDirection.LONG,
            size=Decimal("10"),
            entry_price=Decimal("50000"),
            entry_timestamp=datetime.now(timezone.utc),
            accumulated_funding=Decimal("0"),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
        )
        detector = HybridWhaleDetector([ThresholdStrategy(notional_threshold_usd=100_000)])
        assert await detector.is_whale(position)
        assert await detector.get_whale_score(position) > 0

    asyncio.run(run())
