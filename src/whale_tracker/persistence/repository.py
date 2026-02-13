from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from whale_tracker.persistence.models import WhalePosition
from whale_tracker.positions.models import PositionState


class PositionRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save_position(self, position: PositionState, is_whale: bool, confidence: float) -> None:
        async with self.session_factory() as session:
            stmt = insert(WhalePosition).values(
                wallet_address=position.wallet,
                market=position.market,
                position_id=position.get_id(),
                open_datetime=position.entry_timestamp,
                direction=position.direction.value,
                entry_price=float(position.entry_price),
                size=float(position.size),
                notional_usd=float(position.size * position.entry_price),
                realized_pnl=float(position.realized_pnl),
                unrealized_pnl=float(position.unrealized_pnl),
                funding_accumulated=float(position.accumulated_funding),
                is_liquidated=position.is_liquidated,
                is_whale=is_whale,
                whale_confidence=confidence,
            ).on_conflict_do_update(index_elements=["position_id"], set_={"updated_at": datetime.utcnow(), "is_whale": is_whale, "whale_confidence": confidence})
            await session.execute(stmt)
            await session.commit()

    async def get_whale_positions(self, limit: int = 100, since: datetime | None = None):
        async with self.session_factory() as session:
            stmt = select(WhalePosition).where(WhalePosition.is_whale.is_(True))
            if since:
                stmt = stmt.where(WhalePosition.open_datetime >= since)
            stmt = stmt.order_by(WhalePosition.open_datetime.desc()).limit(limit)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def get_last_fill_timestamp(self, wallet: str):
        async with self.session_factory() as session:
            stmt = select(WhalePosition.open_datetime).where(WhalePosition.wallet_address == wallet).order_by(WhalePosition.open_datetime.desc()).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
