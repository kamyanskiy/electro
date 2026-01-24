from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.models.user import User
from app.core.ports.users import UsersRepository


class SqlAlchemyUsersRepository(UsersRepository):
    """SQLAlchemy ORM implementation of UsersRepository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def get(self, id: UUID) -> User | None:
        """Get user by ID."""
        async with self.session_factory() as session:
            return await session.get(User, id)

    async def get_by_plot_number(self, plot_number: str) -> User | None:
        """Get user by plot number."""
        async with self.session_factory() as session:
            stmt = select(User).where(User.plot_number == plot_number)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        async with self.session_factory() as session:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def add(self, user: User):
        """Add new user to database."""
        async with self.session_factory() as session:
            session.add(user)
            await session.commit()

    async def update(self, user: User):
        """Update existing user."""
        async with self.session_factory() as session:
            await session.merge(user)
            await session.commit()

    async def get_inactive_users(self) -> list[User]:
        """Get all inactive users (for admin activation)."""
        async with self.session_factory() as session:
            stmt = select(User).where(User.is_active == False)
            result = await session.execute(stmt)
            return list(result.scalars().all())