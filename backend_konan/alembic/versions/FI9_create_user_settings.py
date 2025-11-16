"""FI9_create_user_settings - Table user_settings pour préférences utilisateur"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration FI9
revision = 'FI9_user_settings_20251116'
down_revision = 'FI9_messages_20251116'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table user_settings existe déjà
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'user_settings'
        )
    """))
    if result.scalar():
        print("[FI9] Table user_settings existe déjà, migration ignorée")
        return
    
    # Créer table user_settings
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('language', sa.String(10), nullable=True, server_default='fr', comment='Langue préférée'),
        sa.Column('theme', sa.String(20), nullable=True, server_default='light', comment='Thème UI'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('preferences', sa.JSON(), nullable=True, comment='Préférences JSON additionnelles'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    
    # Index (vérifier existence avant création)
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'user_settings' 
            AND indexname = 'ix_user_settings_user_id'
        )
    """))
    if not result_idx.scalar():
        op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'], unique=True)

def downgrade():
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')
    op.drop_table('user_settings')

