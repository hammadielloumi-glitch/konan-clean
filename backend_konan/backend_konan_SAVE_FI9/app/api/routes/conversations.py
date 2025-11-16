# ============================================
# app/api/routes/conversations.py
# ============================================

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.conversation import Conversation
from app.core.security import verify_jwt

router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
    dependencies=[Depends(verify_jwt)]
)


# ======================================================
# 🔹 GET /api/conversations — liste paginée
# ======================================================
@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = None,
):
    q = db.query(Conversation).order_by(Conversation.created_at.desc())
    if cursor:
        try:
            ts = datetime.fromisoformat(cursor)
            q = q.filter(Conversation.created_at < ts)
        except Exception:
            pass
    items = q.limit(limit).all()
    next_cursor = items[-1].created_at.isoformat() if len(items) == limit else None

    return {
        "items": [
            {
                "id": c.id,
                "title": c.message_user,
                "message_user": c.message_user,  # 🔹 pour compatibilité test
                "role": c.role,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in items
        ],
        "next_cursor": next_cursor,
    }

# ======================================================
# 🔹 POST /api/conversations — création
# ======================================================
@router.post("")
async def create_conversation(request: Request, db: Session = Depends(get_db)):
    """Crée une nouvelle conversation, en lisant le titre du JSON reçu."""
    payload = await request.json()
    title = payload.get("title") if isinstance(payload, dict) else None

    conv = Conversation(
        session_id="local",
        message_user=title or "Nouvelle conversation",
        message_konan=None,
    )

    db.add(conv)
    db.commit()
    db.refresh(conv)

    return {
        "id": conv.id,
        "title": conv.message_user,
        "created_at": conv.created_at.isoformat(),
    }


# ======================================================
# 🔹 PATCH /api/conversations/{id} — mise à jour du titre
# ======================================================
@router.patch("/{conv_id}")
def update_conversation(conv_id: int, data: dict, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    if "title" in data:
        conv.message_user = data["title"]

    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "title": conv.message_user}


# ======================================================
# 🔹 DELETE /api/conversations/{id} — suppression
# ======================================================
@router.delete("/{conv_id}")
def delete_conversation(conv_id: int, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")
    db.delete(conv)
    db.commit()
    return {"status": "deleted"}


# ======================================================
# 🔹 GET /api/conversations/{id}/messages — messages liés
# ======================================================
@router.get("/{conv_id}/messages")
def get_conversation_messages(
    conv_id: int,
    db: Session = Depends(get_db),
    limit: int = 100,
    cursor: Optional[str] = None,
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    data = {
        "items": [
            {
                "id": conv.id,
                "role": conv.role,
                "content": conv.message_user,
                "response": conv.message_konan,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
            }
        ],
        "next_cursor": None,
    }
    return data
