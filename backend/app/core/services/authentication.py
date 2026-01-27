from datetime import datetime, timedelta, UTC
from jose import jwt
import bcrypt
from config.settings import settings
from app.core.ports.users import UsersRepository
from app.core.models.user import User


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt


class AuthenticationService:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def authenticate(self, username: str, password: str) -> tuple[str, User]:
        """Authenticate user and return JWT token and user object."""
        # Get user by username or email
        user = await self.users_repo.get_by_username(username)
        if not user:
            # Try to get user by email if username not found
            user = await self.users_repo.get_by_email(username)

        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        # Generate JWT token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value}
        )

        return access_token, user