"""
Modèle Conversation Mode C Supabase – FI9_NAYEK v12.1
- Lié à User via user_id
- Supporte messages multiples via relation Message
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Conversation(Base):
    """
    Modèle Conversation Mode C Supabase
    - user_id: FK vers users.id
    - session_id: ID de session unique
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True, comment='ID de session unique')
    title = Column(String(500), nullable=True, comment='Titre de la conversation')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

