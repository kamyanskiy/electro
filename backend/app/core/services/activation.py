from app.core.models.user import UserRole
from app.core.ports.uow import ActivationUnitOfWork
from uuid import UUID
from datetime import datetime, UTC


class ActivationService:
    def __init__(self, uow: ActivationUnitOfWork):
        self.uow = uow

    async def activate_user(self, user_id: UUID, admin_id: UUID):
        async with self.uow as uow:
            # Check admin privileges (read-only, no lock needed)
            admin = await uow.get_user(admin_id)
            if not admin or admin.role != UserRole.ADMIN:
                raise PermissionError("Only admins can activate users")

            # Get user with lock to prevent concurrent activations
            user = await uow.get_user_for_update(user_id)
            if not user:
                raise ValueError("User not found")

            if user.is_active:
                raise ValueError("User already activated")

            # Update user
            user.is_active = True
            user.activated_at = datetime.now(UTC)
            await uow.update_user(user)

            # Create activation record
            await uow.add_activation_record(
                user_id=user_id,
                activated_by=admin_id,
            )

            # Commit both atomically
            await uow.commit()

        return user

    async def get_pending_users(self):
        async with self.uow as uow:
            return await uow.get_inactive_users()
