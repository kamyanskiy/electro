from abc import ABC, abstractmethod
from uuid import UUID

from app.core.models.user import User


class ActivationUnitOfWork(ABC):
    """Unit of Work for activation operations.

    Groups user update and activation record creation
    into a single atomic transaction.
    """

    @abstractmethod
    async def __aenter__(self) -> "ActivationUnitOfWork":
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    @abstractmethod
    async def get_user(self, user_id: UUID) -> User | None:
        """Get user by ID within this transaction (read-only)."""
        ...

    @abstractmethod
    async def get_user_for_update(self, user_id: UUID) -> User | None:
        """Get user by ID with row-level lock for safe mutation."""
        ...

    @abstractmethod
    async def update_user(self, user: User) -> None:
        """Update user within this transaction (no commit)."""
        ...

    @abstractmethod
    async def add_activation_record(
        self, user_id: UUID, activated_by: UUID
    ) -> None:
        """Create activation record within this transaction (no commit)."""
        ...

    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes atomically."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback all changes."""
        ...
