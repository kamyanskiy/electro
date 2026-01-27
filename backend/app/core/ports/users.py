from abc import ABC, abstractmethod
from uuid import UUID
from app.core.models.user import User

class UsersRepository(ABC):
    @abstractmethod
    async def get(self, id: UUID) -> User | None:
        """Get user by ID."""
        ...

    @abstractmethod
    async def get_by_plot_number(self, plot_number: str) -> User | None:
        """Get user by plot number."""
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        ...

    @abstractmethod
    async def add(self, user: User):
        """Add new user to database."""
        ...

    @abstractmethod
    async def update(self, user: User):
        """Update existing user."""
        ...

    @abstractmethod
    async def get_inactive_users(self) -> list[User]:
        """Get all inactive users (for admin activation)."""
        ...