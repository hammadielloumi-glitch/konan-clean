from alembic import op
import sqlalchemy as sa

revision = 'fix_alembic_len'
down_revision = 'f5d11b45e90c'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column(
        'alembic_version',
        'version_num',
        type_=sa.String(128),
        existing_type=sa.String(32)
    )

def downgrade():
    op.alter_column(
        'alembic_version',
        'version_num',
        type_=sa.String(32),
        existing_type=sa.String(128)
    )
