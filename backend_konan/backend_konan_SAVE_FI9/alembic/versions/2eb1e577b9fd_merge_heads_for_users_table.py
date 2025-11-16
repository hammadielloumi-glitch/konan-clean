"""merge heads for users table

Revision ID: 2eb1e577b9fd
Revises: 825095e952d3_add_users_table_manually
Create Date: 2025-10-21 10:38:16.979714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2eb1e577b9fd'
down_revision: Union[str, Sequence[str], None] = '825095e952d3_add_users_table_manually'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
