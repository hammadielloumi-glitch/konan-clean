"""FI9_patch_users_structure - Patch table users existante pour Mode C Supabase"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Identifiants de migration FI9
revision = 'FI9_patch_users_structure_20251116'
down_revision = 'FI9_users_mode_c_20251116'  # Après la migration users
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table users existe
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'users'
        )
    """))
    if not result.scalar():
        print("[FI9] Table users n'existe pas, migration ignorée")
        return
    
    # Créer enum plan_type si n'existe pas (avec valeurs FI9)
    plan_type_enum = postgresql.ENUM('FREE', 'PRO', 'LEGAL_PLUS', name='plan_type', create_type=False)
    plan_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Vérifier et ajouter colonne supabase_id
    result_col = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'users' 
            AND column_name = 'supabase_id'
        )
    """))
    if not result_col.scalar():
        print("[FI9] Ajout de la colonne supabase_id à users")
        op.add_column('users', sa.Column('supabase_id', sa.String(255), nullable=True))
        # Mettre à jour les valeurs NULL avec un placeholder temporaire
        conn.execute(sa.text("UPDATE users SET supabase_id = 'temp_' || id::text WHERE supabase_id IS NULL"))
        # Rendre NOT NULL après avoir rempli les valeurs
        op.alter_column('users', 'supabase_id', nullable=False)
        # Créer index unique
        op.create_index('ix_users_supabase_id', 'users', ['supabase_id'], unique=True)
        # Créer contrainte unique
        op.create_unique_constraint('uq_users_supabase_id', 'users', ['supabase_id'])
    
    # Vérifier et ajouter colonne role
    result_col = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'users' 
            AND column_name = 'role'
        )
    """))
    if not result_col.scalar():
        print("[FI9] Ajout de la colonne role à users")
        op.add_column('users', sa.Column('role', sa.String(50), nullable=True, server_default='user'))
    
    # Vérifier et ajouter colonne updated_at
    result_col = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'users' 
            AND column_name = 'updated_at'
        )
    """))
    if not result_col.scalar():
        print("[FI9] Ajout de la colonne updated_at à users")
        op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), 
                                         server_default=sa.func.now(), nullable=False))
    
    # Vérifier et modifier colonne plan pour utiliser enum plan_type FI9
    result_col = conn.execute(sa.text("""
        SELECT data_type FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'plan'
    """))
    plan_type = result_col.scalar()
    if plan_type and plan_type != 'USER-DEFINED':
        print("[FI9] Conversion de la colonne plan vers enum plan_type")
        # Convertir les valeurs existantes
        conn.execute(sa.text("""
            UPDATE users SET plan = 'FREE' WHERE plan = 'Free' OR plan IS NULL
        """))
        conn.execute(sa.text("""
            UPDATE users SET plan = 'PRO' WHERE plan = 'Pro'
        """))
        conn.execute(sa.text("""
            UPDATE users SET plan = 'LEGAL_PLUS' WHERE plan = 'Legal+'
        """))
        # Changer le type de colonne
        op.alter_column('users', 'plan', 
                       type_=postgresql.ENUM('FREE', 'PRO', 'LEGAL_PLUS', name='plan_type'),
                       postgresql_using='plan::text::plan_type',
                       nullable=False,
                       server_default='FREE')
    
    # Vérifier et créer index ix_users_email si manquant
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'users' 
            AND indexname = 'ix_users_email'
        )
    """))
    if not result_idx.scalar():
        print("[FI9] Création de l'index ix_users_email")
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Vérifier contrainte unique sur email
    result_uq = conn.execute(sa.text("""
        SELECT COUNT(*) FROM information_schema.table_constraints 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND constraint_type = 'UNIQUE'
        AND constraint_name LIKE '%email%'
    """))
    if result_uq.scalar() == 0:
        print("[FI9] Création de la contrainte unique sur email")
        op.create_unique_constraint('uq_users_email', 'users', ['email'])
    
    # Corriger nullability des colonnes existantes
    # is_active: nullable=False, default=true
    result_col = conn.execute(sa.text("""
        SELECT is_nullable FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'is_active'
    """))
    if result_col.scalar() == 'YES':
        print("[FI9] Correction nullability de is_active")
        conn.execute(sa.text("UPDATE users SET is_active = true WHERE is_active IS NULL"))
        op.alter_column('users', 'is_active', nullable=False, server_default='true')
    
    # created_at: nullable=False
    result_col = conn.execute(sa.text("""
        SELECT is_nullable FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'created_at'
    """))
    if result_col.scalar() == 'YES':
        print("[FI9] Correction nullability de created_at")
        conn.execute(sa.text("UPDATE users SET created_at = now() WHERE created_at IS NULL"))
        op.alter_column('users', 'created_at', nullable=False, server_default=sa.func.now())
    
    # plan: nullable=False
    result_col = conn.execute(sa.text("""
        SELECT is_nullable FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND column_name = 'plan'
    """))
    if result_col.scalar() == 'YES':
        print("[FI9] Correction nullability de plan")
        conn.execute(sa.text("UPDATE users SET plan = 'FREE' WHERE plan IS NULL"))
        op.alter_column('users', 'plan', nullable=False, server_default='FREE')

def downgrade():
    # Ne pas supprimer les colonnes pour éviter la perte de données
    # Seulement supprimer les index et contraintes ajoutés
    conn = op.get_bind()
    
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'users' 
            AND indexname = 'ix_users_supabase_id'
        )
    """))
    if result_idx.scalar():
        op.drop_index('ix_users_supabase_id', table_name='users')
    
    result_uq = conn.execute(sa.text("""
        SELECT constraint_name FROM information_schema.table_constraints 
        WHERE table_schema = 'public' 
        AND table_name = 'users' 
        AND constraint_type = 'UNIQUE'
        AND constraint_name = 'uq_users_supabase_id'
    """))
    uq_name = result_uq.scalar()
    if uq_name:
        op.drop_constraint('uq_users_supabase_id', 'users', type_='unique')

