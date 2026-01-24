from dataclasses import dataclass
from uuid import UUID
from datetime import datetime, UTC
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

@dataclass
class User:
    id: UUID
    plot_number: str
    username: str
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    is_active: bool = False
    created_at: datetime | None = None
    activated_at: datetime | None = None