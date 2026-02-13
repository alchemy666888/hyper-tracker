from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class NormalizedEvent:
    event_type: str
    wallet: str
    market: str
    timestamp: datetime
    data: dict
    idempotency_key: str


class EventNormalizer:
    def __init__(self, max_entries: int = 100_000, max_age: timedelta = timedelta(minutes=5)):
        self.max_entries = max_entries
        self.max_age = max_age
        self._seen: dict[str, datetime] = {}

    def get_idempotency_key(self, event: dict) -> str:
        data = event.get("data", {})
        return str(data.get("id") or event.get("id") or f"{event.get('channel')}:{data.get('time')}:{data.get('user')}:{data.get('coin')}")

    def normalize(self, raw_event: dict) -> NormalizedEvent:
        data = raw_event.get("data", {})
        ts = data.get("time") or raw_event.get("time")
        timestamp = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if isinstance(ts, (int, float)) else datetime.now(timezone.utc)
        return NormalizedEvent(
            event_type=raw_event.get("channel", "unknown"),
            wallet=data.get("user", ""),
            market=data.get("coin", ""),
            timestamp=timestamp,
            data=data,
            idempotency_key=self.get_idempotency_key(raw_event),
        )

    def is_duplicate(self, event: NormalizedEvent) -> bool:
        self._cleanup()
        if event.idempotency_key in self._seen:
            return True
        self._seen[event.idempotency_key] = event.timestamp
        if len(self._seen) > self.max_entries:
            self._seen.pop(next(iter(self._seen)))
        return False

    def _cleanup(self) -> None:
        cutoff = datetime.now(timezone.utc) - self.max_age
        keys = [k for k, ts in self._seen.items() if ts < cutoff]
        for key in keys:
            del self._seen[key]
