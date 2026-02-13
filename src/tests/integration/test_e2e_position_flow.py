from datetime import datetime, timezone
from decimal import Decimal

from whale_tracker.events.models import Fill
from whale_tracker.positions.models import PositionState
from whale_tracker.positions.state_machine import PositionStateMachine


def test_e2e_position_flow():
    machine = PositionStateMachine()
    state = PositionState.empty(wallet="0xabc", market="BTC")
    for side, size, price in [
        ("buy", "1", "45000"),
        ("buy", "1", "46000"),
        ("sell", "2", "47000"),
    ]:
        state = machine.process_fill(
            state,
            Fill(
                wallet="0xabc",
                market="BTC",
                side=side,
                size=Decimal(size),
                price=Decimal(price),
                timestamp=datetime.now(timezone.utc),
            ),
        )
    assert state.size == 0
    assert state.realized_pnl > 0
