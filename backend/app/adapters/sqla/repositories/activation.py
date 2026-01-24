from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.ports.activation import ActivationRequestsRepository
from app.adapters.sqla.mapping.tables import activation_requests


class SqlAlchemyActivationRequestsRepository(ActivationRequestsRepository):
    """SQLAlchemy implementation of ActivationRequestsRepository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def add_activation_record(self, user_id: UUID, activated_by: UUID):
        """Add activation record when admin activates a user."""
        async with self.session_factory() as session:
            now = datetime.now(UTC)
            stmt = activation_requests.insert().values(
                user_id=user_id,
                requested_at=now,  # For admin activations, request time = activation time
                activated_at=now,
                activated_by=activated_by
            )
            await session.execute(stmt)
            await session.commit()

    async def get_activation_history(self, user_id: UUID) -> list[dict]:
        """Get activation history for a user."""
        async with self.session_factory() as session:
            stmt = (
                select(activation_requests)
                .where(activation_requests.c.user_id == user_id)
            )
            result = await session.execute(stmt)
            rows = result.fetchall()

            return [
                {
                    "id": row.id,
                    "user_id": row.user_id,
                    "requested_at": row.requested_at,
                    "activated_at": row.activated_at,
                    "activated_by": row.activated_by
                }
                for row in rows
            ]