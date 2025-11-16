"""
Modèle UserSettings – FI9_NAYEK v12.1
- Préférences utilisateur
- Un seul settings par user (1:1)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserSettings(Base):
    """
    Modèle UserSettings
    - user_id: FK vers users.id (unique)
    - Préférences utilisateur
    """
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    language = Column(String(10), nullable=True, server_default='fr', comment='Langue préférée')
    theme = Column(String(20), nullable=True, server_default='light', comment='Thème UI')
    notifications_enabled = Column(Boolean, nullable=False, server_default='true')
    preferences = Column(JSON, nullable=True, comment='Préférences JSON additionnelles')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="settings")

