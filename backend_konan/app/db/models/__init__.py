"""
Modèles DB Mode C Supabase – FI9_NAYEK v12.1
"""
from app.db.models.user import User, PlanType
from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.user_settings import UserSettings
from app.db.models.audit_log import AuditLog
from app.db.models.legal_search_history import LegalSearchHistory

__all__ = [
    "User",
    "PlanType",
    "Conversation",
    "Message",
    "UserSettings",
    "AuditLog",
    "LegalSearchHistory",
]

