"""Merge heads: 44eef51b39f3 and a1b2c3d4e5f6

Revision ID: b7c8d9e0f123
Revises: 44eef51b39f3, a1b2c3d4e5f6
Create Date: 2025-12-02 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f123'
down_revision: Union[str, Sequence[str], None] = ('44eef51b39f3', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge migration: no DB changes; resolves multiple heads."""
    # This is a merge revision: it records that the two divergent
    # branches have been reconciled. No schema operations required.
    pass


def downgrade() -> None:
    # Downgrade is a no-op for merge revisions.
    pass
