"""FI9_create_users_mode_c - Table users adaptée Mode C Supabase"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identifiants de migration FI9
revision = 'FI9_users_mode_c_20251116'
down_revision = '20251109_merge_heads_after_laws_and_files'  # Dernière migration existante
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table users existe déjà
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        )
    """))
    table_exists = result.scalar()
    
    if table_exists:
        print("[FI9] Table users existe déjà, migration ignorée")
        # Vérifier si la colonne supabase_id existe, sinon l'ajouter
        result_col = conn.execute(sa.text("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'users' 
                AND column_name = 'supabase_id'
            )
        """))
        if not result_col.scalar():
            print("[FI9] Ajout de la colonne supabase_id à la table users existante")
            op.add_column('users', sa.Column('supabase_id', sa.String(255), nullable=True))
            op.create_index('ix_users_supabase_id', 'users', ['supabase_id'], unique=True)
        return
    
    # Créer enum plan_type si n'existe pas
    plan_type_enum = postgresql.ENUM('FREE', 'PRO', 'LEGAL_PLUS', name='plan_type', create_type=False)
    plan_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Créer table users Mode C
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('supabase_id', sa.String(255), nullable=False, unique=True, index=True, comment='ID Supabase (sub du JWT)'),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), nullable=True, server_default='user', comment='Role depuis app_metadata'),
        sa.Column('plan', plan_type_enum, nullable=False, server_default='FREE'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supabase_id'),
        sa.UniqueConstraint('email')
    )
    
    # Index pour recherche rapide
    op.create_index('ix_users_supabase_id', 'users', ['supabase_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_supabase_id', table_name='users')
    op.drop_table('users')
    # Ne pas supprimer l'enum car peut être utilisé ailleurs
    # op.execute("DROP TYPE IF EXISTS plan_type")

