"""Table definitions."""

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    text,
    Numeric,
    Date,
)
from sqlalchemy.sql import func

from .types import UUID, UserRoleType

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("gen_random_uuid()")),
    Column("plot_number", String, nullable=False),
    Column("username", String, nullable=False, unique=True),
    Column("email", String, nullable=False, unique=True),
    Column("password_hash", String, nullable=False),
    Column("role", UserRoleType, nullable=False, default="user"),
    Column("is_active", Boolean, nullable=False, default=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("activated_at", DateTime(timezone=True), nullable=True, default=None),
    CheckConstraint("role IN ('admin', 'user')", name="check_valid_role"),
)

readings = Table(
    "readings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("day_reading", Numeric(10, 2), nullable=False),
    Column("night_reading", Numeric(10, 2), nullable=False),
    Column("reading_date", Date, nullable=False),
)

activation_requests = Table(
    "activation_requests",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("requested_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("activated_at", DateTime(timezone=True), nullable=True),
    Column("activated_by", UUID, ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
)