"""FI9_create_conversations_mode_c - Table conversations adaptée Mode C Supabase"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration FI9
revision = 'FI9_conversations_mode_c_20251116'
down_revision = 'FI9_users_mode_c_20251116'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table conversations existe déjà
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'conversations'
        )
    """))
    if result.scalar():
        print("[FI9] Table conversations existe déjà, migration ignorée")
        return
    
    # Créer table conversations Mode C
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('session_id', sa.String(255), nullable=False, index=True, comment='ID de session unique'),
        sa.Column('title', sa.String(500), nullable=True, comment='Titre de la conversation'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Index pour recherche rapide
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_conversations_session_id', 'conversations', ['session_id'])

def downgrade():
    op.drop_index('ix_conversations_session_id', table_name='conversations')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')

