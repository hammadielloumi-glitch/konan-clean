"""FI9_create_audit_logs - Table audit_logs pour traçabilité"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration FI9
revision = 'FI9_audit_logs_20251116'
down_revision = 'FI9_user_settings_20251116'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table audit_logs existe déjà
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'audit_logs'
        )
    """))
    if result.scalar():
        print("[FI9] Table audit_logs existe déjà, migration ignorée")
        return
    
    # Créer table audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('action', sa.String(100), nullable=False, comment='Type d\'action: login, logout, create, update, delete'),
        sa.Column('resource_type', sa.String(100), nullable=True, comment='Type de ressource: conversation, message, file'),
        sa.Column('resource_id', sa.Integer(), nullable=True, comment='ID de la ressource'),
        sa.Column('ip_address', sa.String(45), nullable=True, comment='Adresse IP'),
        sa.Column('user_agent', sa.String(500), nullable=True, comment='User Agent'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='Métadonnées additionnelles'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Index pour recherche rapide (vérifier existence avant création)
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'audit_logs' 
            AND indexname = 'ix_audit_logs_user_id'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'audit_logs' 
            AND indexname = 'ix_audit_logs_action'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'audit_logs' 
            AND indexname = 'ix_audit_logs_created_at'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

def downgrade():
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')

