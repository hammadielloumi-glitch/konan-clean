"""
Initialisation DB Mode C Supabase – FI9_NAYEK v12.1
- Création des tables
- Initialisation des données de base
"""
from app.database import engine, Base
from app.db.models import User, Conversation, Message, UserSettings, AuditLog, LegalSearchHistory


def init_db():
    """
    Initialise la base de données en créant toutes les tables.
    À utiliser uniquement en développement ou pour migrations initiales.
    """
    Base.metadata.create_all(bind=engine)
    print("[FI9] Base de données initialisée")


if __name__ == "__main__":
    init_db()

