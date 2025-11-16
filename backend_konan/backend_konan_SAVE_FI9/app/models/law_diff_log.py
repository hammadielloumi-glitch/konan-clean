# ============================================
# app/models/law_diff_log.py — Historique des comparaisons de lois
# ============================================
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class LawDiffLog(Base):
    __tablename__ = "law_diff_log"

    id = Column(Integer, primary_key=True, index=True)
    validator = Column(String(100), nullable=False)
    added_count = Column(Integer, default=0)
    removed_count = Column(Integer, default=0)
    diff_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
