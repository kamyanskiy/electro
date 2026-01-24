from abc import ABC, abstractmethod
from uuid import UUID

class ActivationRequestsRepository(ABC):
    @abstractmethod
    async def add_activation_record(self, user_id: UUID, activated_by: UUID):
        ...
    
    @abstractmethod
    async def get_activation_history(self, user_id: UUID) -> list[dict]:
        ...