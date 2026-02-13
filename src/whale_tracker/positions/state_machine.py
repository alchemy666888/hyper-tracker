from dataclasses import replace
from decimal import Decimal

from whale_tracker.events.models import Fill, FundingEvent, LiquidationEvent
from whale_tracker.positions.models import PositionDirection, PositionState


class PositionStateMachine:
    def process_fill(self, state: PositionState, fill: Fill) -> PositionState:
        signed_size = fill.size if fill.side.lower() == "buy" else -fill.size
        if not state.is_open():
            return replace(
                state,
                direction=PositionDirection.LONG if signed_size > 0 else PositionDirection.SHORT,
                size=abs(signed_size),
                entry_price=fill.price,
                entry_timestamp=fill.timestamp,
            )

        direction_sign = Decimal("1") if state.direction == PositionDirection.LONG else Decimal("-1")
        current_signed = state.size * direction_sign
        new_signed = current_signed + signed_size

        if current_signed * new_signed > 0 and abs(new_signed) >= abs(current_signed):
            new_size = abs(new_signed)
            weighted = ((state.entry_price * state.size) + (fill.price * abs(signed_size))) / new_size
            return replace(state, size=new_size, entry_price=weighted)

        closed_qty = min(abs(signed_size), state.size)
        pnl = (fill.price - state.entry_price) * closed_qty * direction_sign
        remaining_signed = new_signed
        if remaining_signed == 0:
            return replace(state, size=Decimal("0"), realized_pnl=state.realized_pnl + pnl)
        if current_signed * remaining_signed > 0:
            return replace(state, size=abs(remaining_signed), realized_pnl=state.realized_pnl + pnl)
        return replace(
            state,
            direction=PositionDirection.LONG if remaining_signed > 0 else PositionDirection.SHORT,
            size=abs(remaining_signed),
            entry_price=fill.price,
            entry_timestamp=fill.timestamp,
            realized_pnl=state.realized_pnl + pnl,
        )

    def process_funding(self, state: PositionState, funding: FundingEvent) -> PositionState:
        return replace(
            state,
            accumulated_funding=state.accumulated_funding + funding.funding_amount,
            realized_pnl=state.realized_pnl + funding.funding_amount,
        )

    def process_liquidation(self, state: PositionState, liquidation: LiquidationEvent) -> PositionState:
        _ = liquidation
        return replace(state, size=Decimal("0"), is_liquidated=True)
