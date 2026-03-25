from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.models.user import User
from app.core.ports.users import UsersRepository


_CONSTRAINT_ERRORS: dict[str, str] = {
    "uq_users_plot_number": "Plot number already exists",
    "users_username_key": "Username already exists",
    "uq_users_email_lower": "Email already exists",
}

# Fallback keywords for drivers that don't expose constraint_name
_FIELD_ERRORS: dict[str, str] = {
    "plot_number": "Plot number already exists",
    "username": "Username already exists",
    "email": "Email already exists",
}


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

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email (case-insensitive)."""
        async with self.session_factory() as session:
            stmt = select(User).where(func.lower(User.email) == email.lower())
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def add(self, user: User):
        """Add new user to database."""
        # Ensure email is always stored lowercase for consistency
        # with the case-insensitive unique index
        user.email = user.email.strip().lower()
        async with self.session_factory() as session:
            try:
                session.add(user)
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                # Prefer structured constraint_name (asyncpg)
                constraint = getattr(e.orig, "constraint_name", None)
                if constraint and constraint in _CONSTRAINT_ERRORS:
                    raise ValueError(_CONSTRAINT_ERRORS[constraint]) from e
                # Fallback: match field name in error message (driver-portable)
                detail = str(e.orig).lower()
                for field, msg in _FIELD_ERRORS.items():
                    if field in detail:
                        raise ValueError(msg) from e
                raise ValueError("User with these details already exists") from e

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