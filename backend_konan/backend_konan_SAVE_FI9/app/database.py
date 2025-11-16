# ============================================
# app/database.py — Source unique Base SQLAlchemy (FI9_NAYEK)
# ============================================

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator


def ensure_env_loaded():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    current_value = os.getenv("DATABASE_URL")
    bom_key = "\ufeffDATABASE_URL"

    if not current_value and bom_key in os.environ:
        current_value = os.environ[bom_key].strip()
        if current_value:
            os.environ["DATABASE_URL"] = current_value
            del os.environ[bom_key]
            print("⚙️ [Reload Fix] DATABASE_URL corrigé depuis une clé UTF-8 BOM")

    if current_value:
        return

    if os.path.exists(env_path):
        load_dotenv(env_path, override=True, encoding="utf-8-sig")
        if os.getenv("DATABASE_URL"):
            print("⚙️ [Reload Fix] Variables .env rechargées manuellement dans app/database.py")
            return
        raise RuntimeError("❌ DATABASE_URL toujours manquant après chargement du fichier .env")
    raise RuntimeError(f"❌ Fichier .env introuvable à {env_path}")


ensure_env_loaded()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL non défini dans l'environnement après rechargement manuel.")

# ✅ FI9_NAYEK : Source unique Base SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ FI9_NAYEK : Source unique get_db()
def get_db() -> Generator:
    """Générateur de session DB pour FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ FI9_NAYEK : Exports explicites pour compatibilité
__all__ = ["Base", "engine", "SessionLocal", "get_db"]
