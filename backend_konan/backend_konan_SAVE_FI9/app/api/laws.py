# ============================================
# app/api/laws.py — API lois (Phase 4 unifiée)
# ============================================
from fastapi import APIRouter, HTTPException, Query, Header, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db  # ✅ FI9_NAYEK : Source unique
from app.vector.chroma_manager import search_law, index_laws, collection, CHROMA_DIR
import os, json

router = APIRouter(prefix="/api/laws", tags=["Lois tunisiennes"])
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "konan-secure-admin-key")

def require_admin(x_api_key: str = Header(...)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Accès admin requis.")

# --- Recherche vectorielle (priorité Chroma) ---
@router.get("/search")
def search_laws(query: str = Query(..., min_length=2), n: int = Query(3, ge=1, le=10)):
    try:
        results = search_law(query, n_results=n)
        return {"query": query, "total_results": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche: {e}")

# --- Réindexation ---
@router.post("/reindex")
def reindex_laws(x_api_key: str = Header(...)):
    require_admin(x_api_key)
    try:
        index_laws()
        return {"status": "ok", "message": "Réindexation terminée."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Statistiques locales ---
@router.get("/stats")
def stats_laws():
    try:
        data = collection.get()
        total = len(data.get("documents", []))
        return {"status": "ok", "total_articles": total}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ✅ FI9_NAYEK : Utilisation Depends au lieu de next(get_db())
# --- Liste complète depuis PostgreSQL ---
@router.get("/all")
def list_laws(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT id, code_name, article_number, article_title FROM laws LIMIT 100"))
    return [dict(r) for r in result.mappings().all()]

# ✅ FI9_NAYEK : Utilisation Depends au lieu de next(get_db())
# --- Récupération par ID ---
@router.get("/{law_id}")
def get_law_by_id(law_id: int, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT * FROM laws WHERE id = :id"), {"id": law_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Loi ID {law_id} introuvable")
    return dict(row)
