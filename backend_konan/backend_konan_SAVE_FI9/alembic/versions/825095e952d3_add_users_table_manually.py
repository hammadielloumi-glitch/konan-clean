from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

# Révision
revision = '825095e952d3_add_users_table_manually'
down_revision = 'f5d11b45e90c'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('full_name', sa.String, nullable=True),
        sa.Column('plan', sa.Enum('Free', 'Pro', 'Legal+', name='plan_type'), server_default='Free'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('users')
