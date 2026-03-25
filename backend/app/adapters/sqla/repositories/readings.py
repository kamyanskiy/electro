from uuid import UUID
from datetime import date
from sqlalchemy import select, extract, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.models.reading import Reading
from app.core.models.user import User
from app.core.ports.readings import ReadingsRepository


class SqlAlchemyReadingsRepository(ReadingsRepository):
    """SQLAlchemy ORM implementation of ReadingsRepository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def add(self, reading: Reading):
        """Add new reading to database."""
        async with self.session_factory() as session:
            session.add(reading)
            await session.commit()

    async def get_by_user(self, user_id: UUID, limit: int = 10, offset: int = 0) -> tuple[list[Reading], int]:
        """Get paginated readings and total count atomically."""
        async with self.session_factory() as session:
            total_count = func.count().over().label("total_count")
            stmt = (
                select(Reading, total_count)
                .where(Reading.user_id == user_id)
                .order_by(Reading.reading_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            rows = result.all()

            if not rows:
                # Offset past end — still need accurate total for pagination
                count_stmt = (
                    select(func.count())
                    .select_from(Reading)
                    .where(Reading.user_id == user_id)
                )
                count_result = await session.execute(count_stmt)
                return [], count_result.scalar_one()

            readings = [row[0] for row in rows]
            total = rows[0][1]
            return readings, total

    async def get_by_user_and_date(self, user_id: UUID, reading_date: date) -> Reading | None:
        """Get reading for a specific user and date."""
        async with self.session_factory() as session:
            stmt = (
                select(Reading)
                .where(Reading.user_id == user_id)
                .where(Reading.reading_date == reading_date)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def update(self, reading: Reading):
        """Update existing reading."""
        async with self.session_factory() as session:
            await session.merge(reading)
            await session.commit()

    async def get_all_by_month(self, year: int, month: int) -> list[tuple[Reading, str, str]]:
        """Get all readings for a specific month with user info (plot_number, username)."""
        async with self.session_factory() as session:
            stmt = (
                select(Reading, User.plot_number, User.username)
                .join(User, Reading.user_id == User.id)
                .where(extract('year', Reading.reading_date) == year)
                .where(extract('month', Reading.reading_date) == month)
                .order_by(Reading.reading_date.desc(), User.plot_number)
            )
            result = await session.execute(stmt)
            return list(result.all())

    async def get_all_readings(self) -> list[tuple[Reading, str, str]]:
        """Get all readings with user info (plot_number, username)."""
        async with self.session_factory() as session:
            stmt = (
                select(Reading, User.plot_number, User.username)
                .join(User, Reading.user_id == User.id)
                .order_by(Reading.reading_date.desc(), User.plot_number)
            )
            result = await session.execute(stmt)
            return list(result.all())