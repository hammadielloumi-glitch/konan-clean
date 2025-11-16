"""merge_heads_conversations_fix

Revision ID: 3e88a48b10cc
Revises: 1001_create_conversations_table, dcaa6f7670da
Create Date: 2025-10-23 22:48:14.038213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e88a48b10cc'
down_revision: Union[str, Sequence[str], None] = ('1001_create_conversations_table', 'dcaa6f7670da')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
