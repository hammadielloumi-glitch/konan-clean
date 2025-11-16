"""merge stub and init_legal_schema

Revision ID: f5d11b45e90c
Revises: bd1250b92708, 3de4f71ad3b0
Create Date: 2025-10-20 10:13:50.187755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5d11b45e90c'
down_revision: Union[str, Sequence[str], None] = ('bd1250b92708', '3de4f71ad3b0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
