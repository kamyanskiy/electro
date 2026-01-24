from app.core.models.reading import Reading
from app.core.ports.readings import ReadingsRepository
from app.core.models.user import User
from decimal import Decimal
from datetime import date
from uuid import UUID

class ReadingService:
    def __init__(self, readings_repo: ReadingsRepository):
        self.readings_repo = readings_repo

    async def create_reading(self, day_reading: float, night_reading: float, user: User):
        today = date.today()

        # Check if reading for today already exists
        existing_reading = await self.readings_repo.get_by_user_and_date(user.id, today)

        if existing_reading:
            # Update existing reading
            existing_reading.day_reading = Decimal(str(day_reading))
            existing_reading.night_reading = Decimal(str(night_reading))
            await self.readings_repo.update(existing_reading)
            return existing_reading, True  # Return reading and flag indicating update
        else:
            # Create new reading
            reading = Reading(
                id=0,  # Will be set by database
                user_id=user.id,
                day_reading=Decimal(str(day_reading)),
                night_reading=Decimal(str(night_reading)),
                reading_date=today
            )
            await self.readings_repo.add(reading)
            return reading, False  # Return reading and flag indicating new creation

    async def check_reading_exists_for_today(self, user_id: UUID) -> Reading | None:
        """Check if user has already submitted reading for today."""
        return await self.readings_repo.get_by_user_and_date(user_id, date.today())

    async def get_readings_by_user(self, user_id: UUID, limit: int = 10, offset: int = 0):
        return await self.readings_repo.get_by_user(user_id, limit)

    async def get_all_readings_by_month(self, year: int, month: int):
        """Get all readings for a specific month with user info."""
        return await self.readings_repo.get_all_by_month(year, month)

    async def get_all_readings(self):
        """Get all readings with user info."""
        return await self.readings_repo.get_all_readings()