# ============================================
# app/routers/chat.py — KONAN Assistant Juridique ⚖️
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation
# FI9_NAYEK v12.1 : Import depuis schemas.py (pas schemas/__init__.py)
from app.schemas import ChatRequest, ChatResponse
from app.utils.lang_detector import detect_language
from app.vector.chroma_manager import search_law
from app.memory_vector import store_memory
from app.core.system_prompt import SYSTEM_PROMPT
from app.services.llm_service import call_llm_api
import os, traceback


# ======================================================
# 🔧 INITIALISATION
# ======================================================
# FI9_NAYEK v12.1 : Pas de prefix ici car ajouté dans main.py
router = APIRouter(tags=["chat"])


# ======================================================
# 🧠 RÉCUPÉRATION DE L'HISTORIQUE
# ======================================================
def get_conversation_history(db: Session, session_id: str | None, limit: int = 10):
    """
    Récupère l'historique d'une conversation.
    Retourne une liste vide si session_id est None.
    """
    if not session_id:
        return []
    
    try:
        records = (
            db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.created_at.asc())
            .limit(limit)
            .all()
        )
        history = []
        for rec in records:
            if rec.message_user:
                history.append({"role": "user", "content": rec.message_user})
            if rec.message_konan:
                history.append({"role": "assistant", "content": rec.message_konan})
        return history
    except Exception as e:
        print("[ERREUR HISTORIQUE]", e)
        return []


# ======================================================
# 💬 ENDPOINT PRINCIPAL — CHAT KONAN
# ======================================================
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Assistant juridique KONAN ⚖️
    Gère la conversation complète (détection langue, lois, contexte, historique).
    """
    try:
        # FI9_NAYEK v12.1 : Générer un session_id si None
        # Utiliser getattr pour éviter AttributeError si le schéma n'a pas session_id
        session_id = getattr(request, 'session_id', None) or f"anonymous-{os.urandom(8).hex()}"
        print(f"[MESSAGE RECU] session={session_id} | texte={request.message}")

        # 1️⃣ Détection de la langue
        detected_lang = detect_language(request.message)
        if detected_lang == "ar":
            lang_prompt = "Réponds en arabe tunisien clair, fondé sur le droit tunisien."
        elif detected_lang == "fr":
            lang_prompt = "Réponds en français clair et professionnel."
        else:
            lang_prompt = "Réponds en dialecte tunisien simple, selon le droit tunisien."

        # 2️⃣ Historique
        history = get_conversation_history(db, session_id)

        # 3️⃣ Recherche contextuelle (ChromaDB)
        context_laws = search_law(request.message)
        context_text = "\n\n".join(context_laws) if context_laws else "Aucun texte légal trouvé."

        # 4️⃣ Construction du prompt complet
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": f"Contexte juridique trouvé :\n{context_text}"},
            {"role": "assistant", "content": lang_prompt},
        ] + history + [
            {"role": "user", "content": request.message},
        ]

        # 5️⃣ Requête vers le modèle d’IA
        konan_reply = await call_llm_api(messages)
        konan_reply = konan_reply.strip()

        # 6️⃣ Sauvegarde dans la base
        db.add(Conversation(session_id=session_id, role="user", message_user=request.message))
        db.add(Conversation(session_id=session_id, role="assistant", message_konan=konan_reply))
        db.commit()

        # 7️⃣ Sauvegarde mémoire vectorielle
        store_memory(session_id, request.message, konan_reply)

        print(f"[CHAT OK] Langue detectee={detected_lang}")

        # 8️⃣ Réponse finale
        return {
            "reply": f"⚖️ {konan_reply}",
            "id": session_id,
            "history": [m["content"] for m in messages[-10:]],
        }

    except Exception as e:
        db.rollback()
        print("[ERREUR CHAT]", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


# ======================================================
# 🩺 ROUTE SANTÉ
# ======================================================
@router.get("/health")
def chat_health():
    """
    Vérifie le bon fonctionnement du module chat.
    """
    return {"status": "ok", "message": "KONAN chat-router opérationnel ✅"}
