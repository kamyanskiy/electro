from abc import ABC, abstractmethod
from uuid import UUID
from datetime import date
from app.core.models.reading import Reading

class ReadingsRepository(ABC):
    @abstractmethod
    async def add(self, reading: Reading):
        ...

    @abstractmethod
    async def get_by_user(self, user_id: UUID, limit: int = 10, offset: int = 0) -> tuple[list[Reading], int]:
        """Get paginated readings and total count for a user."""
        ...

    @abstractmethod
    async def get_by_user_and_date(self, user_id: UUID, reading_date: date) -> Reading | None:
        ...

    @abstractmethod
    async def update(self, reading: Reading):
        ...

    @abstractmethod
    async def get_all_by_month(self, year: int, month: int) -> list[tuple[Reading, str, str]]:
        """Get all readings for a specific month with user info (plot_number, username)."""
        ...

    @abstractmethod
    async def get_all_readings(self) -> list[tuple[Reading, str, str]]:
        """Get all readings with user info (plot_number, username)."""
        ...