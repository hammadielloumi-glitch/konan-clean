"""FI9_create_legal_search_history - Table legal_search_history pour historique recherches"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration FI9
revision = 'FI9_legal_search_history_20251116'
down_revision = 'FI9_audit_logs_20251116'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table legal_search_history existe déjà
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'legal_search_history'
        )
    """))
    if result.scalar():
        print("[FI9] Table legal_search_history existe déjà, migration ignorée")
        return
    
    # Créer table legal_search_history
    op.create_table(
        'legal_search_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('query', sa.Text(), nullable=False, comment='Requête de recherche'),
        sa.Column('results_count', sa.Integer(), nullable=True, comment='Nombre de résultats'),
        sa.Column('filters', sa.JSON(), nullable=True, comment='Filtres appliqués'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Index pour recherche rapide (vérifier existence avant création)
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'legal_search_history' 
            AND indexname = 'ix_legal_search_history_user_id'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_legal_search_history_user_id', 'legal_search_history', ['user_id'])
    
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'legal_search_history' 
            AND indexname = 'ix_legal_search_history_created_at'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_legal_search_history_created_at', 'legal_search_history', ['created_at'])

def downgrade():
    op.drop_index('ix_legal_search_history_created_at', table_name='legal_search_history')
    op.drop_index('ix_legal_search_history_user_id', table_name='legal_search_history')
    op.drop_table('legal_search_history')

