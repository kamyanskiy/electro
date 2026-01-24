"""Data types."""

from sqlalchemy import String, TypeDecorator
from sqlalchemy.dialects import postgresql
from app.core.models.user import UserRole

UUID = String().with_variant(postgresql.UUID(as_uuid=True), "postgresql")


class UserRoleType(TypeDecorator):
    """Type decorator that converts between string and UserRole enum."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert UserRole enum to string for database storage."""
        if value is None:
            return None
        if isinstance(value, UserRole):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        """Convert string from database to UserRole enum."""
        if value is None:
            return None
        if isinstance(value, str):
            return UserRole(value)
        return value