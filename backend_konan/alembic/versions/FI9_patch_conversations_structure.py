"""FI9_patch_conversations_structure - Patch table conversations existante pour Mode C Supabase"""
from alembic import op
import sqlalchemy as sa

# Identifiants de migration FI9
revision = 'FI9_patch_conversations_structure_20251116'
down_revision = 'FI9_conversations_mode_c_20251116'  # Après la migration conversations
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    # Vérifier si la table conversations existe
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'conversations'
        )
    """))
    if not result.scalar():
        print("[FI9] Table conversations n'existe pas, migration ignorée")
        return
    
    # Vérifier et ajouter colonne user_id
    result_col = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'conversations' 
            AND column_name = 'user_id'
        )
    """))
    if not result_col.scalar():
        print("[FI9] Ajout de la colonne user_id à conversations")
        # Ajouter colonne nullable d'abord
        op.add_column('conversations', sa.Column('user_id', sa.Integer(), nullable=True))
        # Mettre à jour avec une valeur par défaut (premier utilisateur ou NULL)
        conn.execute(sa.text("""
            UPDATE conversations 
            SET user_id = (SELECT id FROM users LIMIT 1)
            WHERE user_id IS NULL
        """))
        # Créer la foreign key
        op.create_foreign_key('fk_conversations_user_id', 'conversations', 'users', 
                              ['user_id'], ['id'], ondelete='CASCADE')
        # Rendre NOT NULL après avoir rempli les valeurs
        op.alter_column('conversations', 'user_id', nullable=False)
        # Créer index
        op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    
    # Vérifier et ajouter colonne title
    result_col = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'conversations' 
            AND column_name = 'title'
        )
    """))
    if not result_col.scalar():
        print("[FI9] Ajout de la colonne title à conversations")
        op.add_column('conversations', sa.Column('title', sa.String(500), nullable=True))
    
    # Vérifier et ajouter colonne updated_at
    result_col = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'conversations' 
            AND column_name = 'updated_at'
        )
    """))
    if not result_col.scalar():
        print("[FI9] Ajout de la colonne updated_at à conversations")
        op.add_column('conversations', sa.Column('updated_at', sa.DateTime(timezone=True), 
                                                 server_default=sa.func.now(), nullable=False))
    
    # Vérifier et créer index ix_conversations_session_id si manquant
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'conversations' 
            AND indexname = 'ix_conversations_session_id'
        )
    """))
    if not result_idx.scalar():
        print("[FI9] Création de l'index ix_conversations_session_id")
        op.create_index('ix_conversations_session_id', 'conversations', ['session_id'])
    
    # Corriger nullability de created_at
    result_col = conn.execute(sa.text("""
        SELECT is_nullable FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'conversations' 
        AND column_name = 'created_at'
    """))
    if result_col.scalar() == 'YES':
        print("[FI9] Correction nullability de created_at")
        conn.execute(sa.text("UPDATE conversations SET created_at = now() WHERE created_at IS NULL"))
        op.alter_column('conversations', 'created_at', nullable=False, server_default=sa.func.now())

def downgrade():
    # Ne pas supprimer les colonnes pour éviter la perte de données
    # Seulement supprimer les index et contraintes ajoutés
    conn = op.get_bind()
    
    result_fk = conn.execute(sa.text("""
        SELECT constraint_name FROM information_schema.table_constraints 
        WHERE table_schema = 'public' 
        AND table_name = 'conversations' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name = 'fk_conversations_user_id'
    """))
    fk_name = result_fk.scalar()
    if fk_name:
        op.drop_constraint('fk_conversations_user_id', 'conversations', type_='foreignkey')
    
    result_idx = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename = 'conversations' 
            AND indexname = 'ix_conversations_user_id'
        )
    """))
    if result_idx.scalar():
        op.drop_index('ix_conversations_user_id', table_name='conversations')

