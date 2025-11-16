"""FI9_merge_all_heads_20251116 - Merge toutes les branches FI9 en une seule head"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration FI9
revision = 'FI9_merge_all_heads_20251116'
down_revision = (
    'FI9_legal_search_history_20251116',
    'FI9_patch_conversations_structure_20251116',
    'FI9_patch_users_structure_20251116'
)
branch_labels = None
depends_on = None

def upgrade():
    """
    Migration de merge - aucune modification de schéma.
    Cette migration fusionne les 3 branches FI9 :
    - FI9_legal_search_history_20251116 (chaîne principale)
    - FI9_patch_conversations_structure_20251116 (patch conversations)
    - FI9_patch_users_structure_20251116 (patch users)
    """
    pass

def downgrade():
    """
    Downgrade de merge - aucune modification de schéma.
    """
    pass

