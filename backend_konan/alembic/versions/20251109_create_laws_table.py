"""create laws table for legal schema"""
from alembic import op
import sqlalchemy as sa

# Import conditionnel de Vector (pgvector peut ne pas être disponible)
try:
    from pgvector.sqlalchemy import Vector
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    Vector = None

# =====================================================
# Révision Alembic
# =====================================================
revision = "20251109_create_laws_table"
down_revision = "3de4f71ad3b0"
branch_labels = None
depends_on = None

def upgrade():
    # Vérifier d'abord si l'extension vector est disponible dans PostgreSQL
    # Utiliser un SAVEPOINT pour isoler les erreurs et éviter d'annuler la transaction
    conn = op.get_bind()
    vector_available = False
    
    if VECTOR_AVAILABLE:
        try:
            # Vérifier si l'extension existe déjà
            result = conn.execute(sa.text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
            if result.fetchone() is not None:
                vector_available = True
            else:
                # Essayer de créer l'extension avec SAVEPOINT pour isoler l'erreur
                conn.execute(sa.text("SAVEPOINT check_vector_extension"))
                try:
                    conn.execute(sa.text("CREATE EXTENSION vector"))
                    conn.execute(sa.text("RELEASE SAVEPOINT check_vector_extension"))
                    vector_available = True
                except Exception as e:
                    # Rollback vers le savepoint pour continuer la transaction
                    conn.execute(sa.text("ROLLBACK TO SAVEPOINT check_vector_extension"))
                    conn.execute(sa.text("RELEASE SAVEPOINT check_vector_extension"))
                    print(f"[FI9] Extension vector non disponible: {e}")
                    vector_available = False
        except Exception as e:
            print(f"[FI9] Erreur lors de la vérification de l'extension vector: {e}")
            vector_available = False
    
    # Créer table laws avec ou sans colonne vectorielle
    if vector_available and VECTOR_AVAILABLE:
        op.create_table(
            "laws",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("code_name", sa.String(length=255), nullable=False),
            sa.Column("article_number", sa.String(length=50), nullable=False),
            sa.Column("article_title", sa.Text, nullable=True),
            sa.Column("article_text", sa.Text, nullable=False),
            sa.Column("chapter", sa.String(length=255), nullable=True),
            sa.Column("keywords", sa.ARRAY(sa.Text), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=True),
            sa.Column("date_entry", sa.Date, nullable=True),
            sa.Column("source_url", sa.Text, nullable=True),
            sa.Column("last_update", sa.TIMESTAMP, server_default=sa.func.now()),
            sa.Column("language", sa.String(length=10), server_default="fr"),
            sa.Column("vector_embedding", Vector(1536)),
        )
    else:
        # Créer table sans colonne vectorielle si extension non disponible
        op.create_table(
            "laws",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("code_name", sa.String(length=255), nullable=False),
            sa.Column("article_number", sa.String(length=50), nullable=False),
            sa.Column("article_title", sa.Text, nullable=True),
            sa.Column("article_text", sa.Text, nullable=False),
            sa.Column("chapter", sa.String(length=255), nullable=True),
            sa.Column("keywords", sa.ARRAY(sa.Text), nullable=True),
            sa.Column("category", sa.String(length=100), nullable=True),
            sa.Column("date_entry", sa.Date, nullable=True),
            sa.Column("source_url", sa.Text, nullable=True),
            sa.Column("last_update", sa.TIMESTAMP, server_default=sa.func.now()),
            sa.Column("language", sa.String(length=10), server_default="fr"),
            # vector_embedding omis si extension non disponible
        )
        print("[FI9] Table laws créée sans colonne vectorielle (extension vector non disponible)")

    # Indexation plein texte
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_laws_text_search ON laws USING GIN (to_tsvector('french', article_text));"
    )
    
    # Index vectoriel uniquement si extension disponible
    if vector_available:
        try:
            op.execute(
                "CREATE INDEX IF NOT EXISTS idx_laws_vector ON laws USING ivfflat (vector_embedding vector_cosine_ops);"
            )
        except Exception as e:
            print(f"[FI9] Index vectoriel non créé: {e}")

def downgrade():
    op.drop_table("laws")
