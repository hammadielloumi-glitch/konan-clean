"""
Modèle Message – FI9_NAYEK v12.1
- Messages individuels pour conversations
- Supporte role: user, assistant, system
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    """
    Modèle Message
    - conversation_id: FK vers conversations.id
    - role: user, assistant, system
    - content: Contenu du message
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(50), nullable=False, comment='user, assistant, system')
    content = Column(Text, nullable=False, comment='Contenu du message')
    metadata = Column(JSON, nullable=True, comment='Métadonnées additionnelles')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    conversation = relationship("Conversation", back_populates="messages")

