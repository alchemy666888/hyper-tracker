from datetime import datetime, timezone
from decimal import Decimal

from whale_tracker.positions.lifecycle import PositionLifecycle
from whale_tracker.positions.models import PositionDirection, PositionState


def test_emit_position_event():
    lifecycle = PositionLifecycle()
    position = PositionState(
        wallet="0xabc",
        market="ETH",
        direction=PositionDirection.LONG,
        size=Decimal("1"),
        entry_price=Decimal("3000"),
        entry_timestamp=datetime.now(timezone.utc),
        accumulated_funding=Decimal("0"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
    )
    event = lifecycle.emit_position_event("opened", position)
    assert event.event_type == "opened"
