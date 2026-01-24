"""ORM mapping - connects domain models to SQLAlchemy tables."""

from sqlalchemy.orm import registry

from app.core.models.user import User, UserRole
from app.core.models.reading import Reading
from app.adapters.sqla.mapping import tables

mapper_registry = registry()
metadata = tables.metadata


def bind_mappers():
    """Binds ORM mappers to domain models."""

    # Map User model to users table
    mapper_registry.map_imperatively(
        User,
        tables.users,
    )

    # Map Reading model to readings table
    mapper_registry.map_imperatively(
        Reading,
        tables.readings,
    )
