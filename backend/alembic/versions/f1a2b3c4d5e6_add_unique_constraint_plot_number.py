"""Add unique constraint to plot_number

Revision ID: f1a2b3c4d5e6
Revises: d22f39b420c8
Create Date: 2026-03-25 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd22f39b420c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint to users.plot_number.

    Checks for duplicate plot_number values first and raises
    an error with guidance if any are found.
    """
    conn = op.get_bind()
    dupes = conn.execute(
        sa.text(
            "SELECT plot_number, COUNT(*) AS cnt "
            "FROM users GROUP BY plot_number HAVING COUNT(*) > 1"
        )
    ).fetchall()
    if dupes:
        dupe_list = ", ".join(f"'{row[0]}' ({row[1]}x)" for row in dupes)
        raise RuntimeError(
            f"Cannot add unique constraint: duplicate plot_number values "
            f"found: {dupe_list}. Resolve duplicates before migrating."
        )
    op.create_unique_constraint(
        'uq_users_plot_number', 'users', ['plot_number']
    )


def downgrade() -> None:
    """Remove unique constraint from users.plot_number."""
    op.drop_constraint('uq_users_plot_number', 'users', type_='unique')
