"""Add unique constraint to plot_number

Revision ID: f1a2b3c4d5e6
Revises: d22f39b420c8
Create Date: 2026-03-25 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'd22f39b420c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint to users.plot_number."""
    op.create_unique_constraint(
        'uq_users_plot_number', 'users', ['plot_number']
    )


def downgrade() -> None:
    """Remove unique constraint from users.plot_number."""
    op.drop_constraint('uq_users_plot_number', 'users', type_='unique')
