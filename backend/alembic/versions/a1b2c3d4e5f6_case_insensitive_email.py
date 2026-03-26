"""Normalize emails to lowercase and add case-insensitive unique index

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-03-25 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Normalize existing emails and switch to case-insensitive unique index."""
    conn = op.get_context().bind

    # Lock table to prevent concurrent registrations during migration
    conn.execute(sa.text("LOCK TABLE users IN EXCLUSIVE MODE"))

    # Check for duplicate emails when lowered
    dupes = conn.execute(
        sa.text(
            "SELECT lower(email) AS em, COUNT(*) AS cnt "
            "FROM users GROUP BY lower(email) HAVING COUNT(*) > 1"
        )
    ).fetchall()
    if dupes:
        dupe_list = ", ".join(f"'{row[0]}' ({row[1]}x)" for row in dupes)
        raise RuntimeError(
            f"Cannot add case-insensitive email index: duplicate emails "
            f"found when lowered: {dupe_list}. Resolve duplicates before migrating."
        )

    # Normalize existing emails to lowercase
    conn.execute(sa.text("UPDATE users SET email = lower(email)"))

    # Drop old case-sensitive unique constraint
    op.drop_constraint('users_email_key', 'users', type_='unique')

    # Add case-insensitive unique index
    op.create_index(
        'uq_users_email_lower', 'users', [sa.text('lower(email)')], unique=True
    )


def downgrade() -> None:
    """Revert to case-sensitive unique constraint.

    NOTE: This does NOT restore original mixed-case email values.
    The upgrade() permanently lowercases all emails. If rollback is
    needed and original casing matters, restore from a DB backup.
    """
    op.drop_index('uq_users_email_lower', 'users')
    op.create_unique_constraint('users_email_key', 'users', ['email'])
