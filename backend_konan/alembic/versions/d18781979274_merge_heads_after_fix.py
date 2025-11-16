from alembic import op

# Identifiants Alembic
revision = 'merge_heads_after_fix'
down_revision = ('3e88a48b10cc', 'fix_alembic_len')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
