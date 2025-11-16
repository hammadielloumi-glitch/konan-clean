# app/routers/laws.py — endpoints de recherche
from fastapi import APIRouter, Query
from app.vector.chroma_manager import search_law

router = APIRouter(prefix="/api/laws", tags=["Laws"])

@router.get("/search", summary="Recherche sémantique dans les lois")
def search_endpoint(q: str = Query(..., min_length=2), n: int = 3):
    return {"query": q, "results": search_law(q, n_results=n)}
