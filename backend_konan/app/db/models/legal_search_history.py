"""
Modèle LegalSearchHistory – FI9_NAYEK v12.1
- Historique des recherches légales
- Lié à User
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class LegalSearchHistory(Base):
    """
    Modèle LegalSearchHistory
    - user_id: FK vers users.id
    - query: Requête de recherche
    - results_count: Nombre de résultats
    - filters: Filtres appliqués
    """
    __tablename__ = "legal_search_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    query = Column(Text, nullable=False, comment='Requête de recherche')
    results_count = Column(Integer, nullable=True, comment='Nombre de résultats')
    filters = Column(JSON, nullable=True, comment='Filtres appliqués')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="legal_search_history")

