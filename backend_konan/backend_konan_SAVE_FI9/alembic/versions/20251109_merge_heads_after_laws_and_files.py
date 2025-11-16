"""merge heads after laws and files"""
from alembic import op

# =====================================================
# Révision Alembic
# =====================================================
revision = "20251109_merge_heads_after_laws_and_files"
down_revision = ("f5c188ee8f8e", "20251109_create_laws_table")  # ← note : singulier ici
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
