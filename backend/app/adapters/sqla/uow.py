from uuid import UUID
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.models.user import User
from app.core.ports.uow import ActivationUnitOfWork
from app.adapters.sqla.mapping.tables import activation_requests


class SqlAlchemyActivationUnitOfWork(ActivationUnitOfWork):
    """SQLAlchemy implementation of ActivationUnitOfWork."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def __aenter__(self) -> "SqlAlchemyActivationUnitOfWork":
        self._session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def get_user(self, user_id: UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def update_user(self, user: User) -> None:
        await self._session.merge(user)

    async def add_activation_record(
        self, user_id: UUID, activated_by: UUID
    ) -> None:
        now = datetime.now(UTC)
        stmt = activation_requests.insert().values(
            user_id=user_id,
            requested_at=now,
            activated_at=now,
            activated_by=activated_by,
        )
        await self._session.execute(stmt)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
