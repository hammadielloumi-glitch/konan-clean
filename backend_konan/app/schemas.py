# =====================================================
# app/schemas.py — Phase 3 stable finale
# =====================================================
from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message utilisateur")
    session_id: Optional[str] = Field(None, description="ID de session")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Réponse de Konan")
    id: Optional[int] = Field(None, description="Identifiant interne")
    history: Optional[List[str]] = Field(default_factory=list, description="Historique des messages")

