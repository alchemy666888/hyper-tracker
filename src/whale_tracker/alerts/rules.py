from abc import ABC, abstractmethod
from datetime import datetime, timezone

from whale_tracker.alerts.base import Alert, AlertSeverity
from whale_tracker.positions.lifecycle import PositionEvent


class AlertRule(ABC):
    @abstractmethod
    async def should_trigger(self, event: PositionEvent) -> Alert | None:
        pass


class WhaleOpenedRule(AlertRule):
    async def should_trigger(self, event: PositionEvent) -> Alert | None:
        if event.event_type != "opened":
            return None
        notional = float(event.position.size * event.position.entry_price)
        if notional > 500_000:
            return Alert(
                severity=AlertSeverity.WARNING,
                title=f"🐳 WHALE OPENED ${notional:,.0f}",
                message=f"{event.position.wallet[:6]}... opened {event.position.size} {event.position.market} @ {event.position.entry_price}",
                data=event.position.__dict__,
                timestamp=datetime.now(timezone.utc),
            )
        return None


class WhaleLiquidatedRule(AlertRule):
    async def should_trigger(self, event: PositionEvent) -> Alert | None:
        if event.event_type != "liquidated":
            return None
        return Alert(
            severity=AlertSeverity.CRITICAL,
            title="💥 WHALE LIQUIDATED",
            message=f"{event.position.wallet[:6]}... liquidated {event.position.size} {event.position.market}",
            data=event.position.__dict__,
            timestamp=datetime.now(timezone.utc),
        )
