# =====================================================
# app/db/session.py — Réexport vers source unique (FI9_NAYEK)
# =====================================================
# ⚠️ DEPRECATED : Utiliser app.database directement
from app.database import Base, engine, SessionLocal, get_db

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
