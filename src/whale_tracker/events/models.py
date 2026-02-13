from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Fill:
    wallet: str
    market: str
    side: str
    size: Decimal
    price: Decimal
    timestamp: datetime


@dataclass(frozen=True)
class FundingEvent:
    wallet: str
    market: str
    funding_rate: Decimal
    funding_amount: Decimal
    timestamp: datetime


@dataclass(frozen=True)
class LiquidationEvent:
    wallet: str
    market: str
    size: Decimal
    price: Decimal
    timestamp: datetime
