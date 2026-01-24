from app.core.models.user import User, UserRole
from app.core.ports.users import UsersRepository
from app.core.ports.activation import ActivationRequestsRepository
from uuid import UUID
from datetime import datetime, UTC

class ActivationService:
    def __init__(
        self,
        users_repo: UsersRepository,
        activation_requests_repo: ActivationRequestsRepository
    ):
        self.users_repo = users_repo
        self.activation_requests_repo = activation_requests_repo
    
    async def activate_user(self, user_id: UUID, admin_id: UUID):
        # Check admin privileges
        admin = await self.users_repo.get(admin_id)
        if not admin or admin.role != UserRole.ADMIN:
            raise PermissionError("Only admins can activate users")
        
        # Get user
        user = await self.users_repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.is_active:
            raise ValueError("User already activated")
        
        # Activate user
        user.is_active = True
        user.activated_at = datetime.now(UTC)
        
        # Create activation record
        await self.activation_requests_repo.add_activation_record(
            user_id=user_id,
            activated_by=admin_id
        )
        
        await self.users_repo.update(user)
        
        return user
    
    async def get_pending_users(self):
        return await self.users_repo.get_inactive_users()