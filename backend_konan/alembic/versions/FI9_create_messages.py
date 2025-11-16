"""FI9_create_messages - Table messages pour conversations"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration FI9
revision = 'FI9_messages_20251116'
down_revision = 'FI9_conversations_mode_c_20251116'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table messages existe déjà
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'messages'
        )
    """))
    if result.scalar():
        print("[FI9] Table messages existe déjà, migration ignorée")
        return
    
    # Créer table messages
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('role', sa.String(50), nullable=False, comment='user, assistant, system'),
        sa.Column('content', sa.Text(), nullable=False, comment='Contenu du message'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='Métadonnées additionnelles'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
    )
    
    # Index pour recherche rapide (vérifier existence avant création)
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'messages' 
            AND indexname = 'ix_messages_conversation_id'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'messages' 
            AND indexname = 'ix_messages_created_at'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_messages_created_at', 'messages', ['created_at'])

def downgrade():
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

