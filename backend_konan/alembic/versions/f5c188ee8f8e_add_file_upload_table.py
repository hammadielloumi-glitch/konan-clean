"""add file_upload table

Revision ID: f5c188ee8f8e
Revises: merge_heads_after_fix
Create Date: 2025-11-08 08:38:31.152021
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Identifiants de révision
revision: str = "f5c188ee8f8e"
down_revision: Union[str, Sequence[str], None] = "merge_heads_after_fix"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Créer la table file_uploads uniquement. Ne toucher à rien d’autre."""
    op.create_table(
        "file_uploads",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("filepath", sa.String(512), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        # décommente si tu ajoutes une FK utilisateur plus tard
        # sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_file_uploads_id", "file_uploads", ["id"], unique=False)


def downgrade() -> None:
    """Supprimer proprement la table et son index."""
    op.drop_index("ix_file_uploads_id", table_name="file_uploads")
    op.drop_table("file_uploads")
