"""create law_diff_log table"""
from alembic import op
import sqlalchemy as sa

revision = "dcaa6f7670da"
down_revision = "2eb1e577b9fd" # ou le dernier id de migration existant
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "law_diff_log",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("validator", sa.String(100), nullable=False),
        sa.Column("added_count", sa.Integer, default=0),
        sa.Column("removed_count", sa.Integer, default=0),
        sa.Column("diff_json", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

def downgrade() -> None:
    op.drop_table("law_diff_log")
