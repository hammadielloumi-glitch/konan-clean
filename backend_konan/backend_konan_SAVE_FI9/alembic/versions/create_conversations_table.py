"""create conversations table"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration
revision = "1001_create_conversations_table"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=True),
        sa.Column("message_user", sa.Text, nullable=True),
        sa.Column("message_konan", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

def downgrade():
    op.drop_table("conversations")
