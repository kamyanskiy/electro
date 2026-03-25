import re

from app.core.models.user import User
from app.core.ports.users import UsersRepository
from uuid import uuid4
from datetime import datetime, UTC
import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class RegistrationService:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    def _validate_password_strength(self, password: str) -> None:
        """Validate password meets minimum requirements."""
        if len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters long"
            )
        if len(password.encode("utf-8")) > 72:
            raise ValueError(
                "Password must not exceed 72 bytes (bcrypt limit)"
            )
        if not re.search(r"[A-Z]", password):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )
        if not re.search(r"\d", password):
            raise ValueError(
                "Password must contain at least one digit"
            )

    async def register_user(self, plot_number: str, username: str, email: str, password: str):
        # Validate password first — reject bad input before DB round-trips
        self._validate_password_strength(password)

        # Pre-check uniqueness for better UX error messages.
        # These checks are racy under concurrent requests;
        # DB UNIQUE constraints are the actual enforcement layer.
        #
        # Check uniqueness of plot number
        existing = await self.users_repo.get_by_plot_number(plot_number)
        if existing:
            raise ValueError("Plot number already exists")

        # Check uniqueness of username
        existing_user = await self.users_repo.get_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")

        # Check uniqueness of email
        existing_email = await self.users_repo.get_by_email(email)
        if existing_email:
            raise ValueError("Email already exists")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = User(
            id=uuid4(),
            plot_number=plot_number,
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(UTC),
            activated_at=None
        )

        # Save
        await self.users_repo.add(user)

        return user