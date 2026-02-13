from datetime import datetime, timezone
from decimal import Decimal

from whale_tracker.events.models import Fill
from whale_tracker.positions.models import PositionState
from whale_tracker.positions.state_machine import PositionStateMachine


def test_position_state_machine_full_lifecycle(wallet: str = "0xabc"):
    machine = PositionStateMachine()
    state = PositionState.empty(wallet=wallet, market="BTC")

    state = machine.process_fill(state, Fill(wallet=wallet, market="BTC", side="buy", size=Decimal("1.0"), price=Decimal("45000"), timestamp=datetime.now(timezone.utc)))
    assert state.size == Decimal("1.0")

    state = machine.process_fill(state, Fill(wallet=wallet, market="BTC", side="buy", size=Decimal("0.5"), price=Decimal("45500"), timestamp=datetime.now(timezone.utc)))
    assert state.size == Decimal("1.5")

    state = machine.process_fill(state, Fill(wallet=wallet, market="BTC", side="sell", size=Decimal("1.0"), price=Decimal("46000"), timestamp=datetime.now(timezone.utc)))
    assert state.size == Decimal("0.5")
    assert state.realized_pnl > 0
