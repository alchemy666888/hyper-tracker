from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class WhalePosition(Base):
    __tablename__ = "whale_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wallet_address: Mapped[str] = mapped_column(String(66), index=True)
    market: Mapped[str] = mapped_column(String(20), index=True)
    position_id: Mapped[str] = mapped_column(String(100), unique=True)
    open_datetime: Mapped[datetime] = mapped_column(DateTime, index=True)
    close_datetime: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)
    direction: Mapped[str] = mapped_column(String(10))
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    size: Mapped[float] = mapped_column(Float)
    notional_usd: Mapped[float] = mapped_column(Float)
    realized_pnl: Mapped[float] = mapped_column(Float)
    unrealized_pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    funding_accumulated: Mapped[float] = mapped_column(Float, default=0.0)
    is_liquidated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_whale: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    whale_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (Index("idx_wallet_market_timestamp", "wallet_address", "market", "open_datetime"),)


class FundingEventORM(Base):
    __tablename__ = "funding_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    market: Mapped[str] = mapped_column(String(20), index=True)
    wallet_address: Mapped[str] = mapped_column(String(66), index=True)
    position_id: Mapped[str] = mapped_column(String(100))
    funding_rate: Mapped[float] = mapped_column(Float)
    funding_amount: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    __table_args__ = (Index("idx_market_timestamp", "market", "timestamp"),)
