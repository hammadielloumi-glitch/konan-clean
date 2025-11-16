# ============================================
# app/schemas/__init__.py — Modèles de base pour l'API Konan
# ============================================
# FI9_NAYEK v12.1 : Schéma corrigé pour correspondre à schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message utilisateur")
    session_id: Optional[str] = Field(None, description="ID de session")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Réponse de Konan")
    id: Optional[str] = Field(None, description="ID de session")
    history: Optional[List[str]] = Field(default_factory=list, description="Historique des messages")
