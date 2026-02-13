from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class PositionDirection(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True)
class PositionState:
    wallet: str
    market: str
    direction: PositionDirection
    size: Decimal
    entry_price: Decimal
    entry_timestamp: datetime
    accumulated_funding: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    is_liquidated: bool = False

    @classmethod
    def empty(cls, wallet: str, market: str) -> "PositionState":
        return cls(
            wallet=wallet,
            market=market,
            direction=PositionDirection.LONG,
            size=Decimal("0"),
            entry_price=Decimal("0"),
            entry_timestamp=datetime.now(timezone.utc),
            accumulated_funding=Decimal("0"),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
        )

    def is_open(self) -> bool:
        return self.size > 0

    def get_id(self) -> str:
        return f"{self.wallet}:{self.market}:{self.entry_timestamp.isoformat()}"
