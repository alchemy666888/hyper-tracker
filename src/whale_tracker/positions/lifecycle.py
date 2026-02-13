from dataclasses import dataclass
from datetime import datetime, timezone

from whale_tracker.positions.models import PositionState


@dataclass(frozen=True)
class PositionEvent:
    event_type: str
    position: PositionState
    metadata: dict | None
    timestamp: datetime


class PositionLifecycle:
    async def record_open(self, position: PositionState) -> None:
        self.emit_position_event("opened", position)

    async def record_update(self, old_state: PositionState, new_state: PositionState) -> None:
        _ = old_state
        self.emit_position_event("updated", new_state)

    async def record_close(self, position: PositionState) -> None:
        self.emit_position_event("closed", position)

    def emit_position_event(self, event_type: str, position: PositionState, metadata: dict | None = None) -> PositionEvent:
        return PositionEvent(event_type=event_type, position=position, metadata=metadata, timestamp=datetime.now(timezone.utc))
