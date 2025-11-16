"""
Modèle User Mode C Supabase – FI9_NAYEK v12.1
- Adapté pour Mode C avec supabase_id
- Compatible avec JWT Supabase
"""
import enum
from sqlalchemy import Column, Integer, String, Enum as PgEnum, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PlanType(str, enum.Enum):
    FREE = "FREE"
    PRO = "PRO"
    LEGAL_PLUS = "LEGAL_PLUS"


class User(Base):
    """
    Modèle User Mode C Supabase
    - supabase_id: ID Supabase (sub du JWT)
    - email: Email utilisateur
    - role: Role depuis app_metadata Supabase
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    supabase_id = Column(String(255), nullable=False, unique=True, index=True, comment='ID Supabase (sub du JWT)')
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=True, server_default='user', comment='Role depuis app_metadata')
    plan = Column(PgEnum(PlanType, name="plan_type"), nullable=False, server_default=PlanType.FREE.value)
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    legal_search_history = relationship("LegalSearchHistory", back_populates="user", cascade="all, delete-orphan")

