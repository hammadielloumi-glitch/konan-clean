"""
Modèle AuditLog – FI9_NAYEK v12.1
- Traçabilité des actions utilisateur
- Insert only via backend
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    """
    Modèle AuditLog
    - user_id: FK vers users.id (nullable pour actions anonymes)
    - action: Type d'action (login, logout, create, update, delete)
    - resource_type: Type de ressource
    - resource_id: ID de la ressource
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = Column(String(100), nullable=False, comment='Type d\'action: login, logout, create, update, delete')
    resource_type = Column(String(100), nullable=True, comment='Type de ressource: conversation, message, file')
    resource_id = Column(Integer, nullable=True, comment='ID de la ressource')
    ip_address = Column(String(45), nullable=True, comment='Adresse IP')
    user_agent = Column(String(500), nullable=True, comment='User Agent')
    metadata = Column(JSON, nullable=True, comment='Métadonnées additionnelles')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="audit_logs")

