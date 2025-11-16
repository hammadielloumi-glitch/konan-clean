from fastapi import APIRouter, Header, HTTPException
from app.vector.index_laws import index_dir
from app.vector.update_scheduler import run_update
import os

router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY","konan-secure-admin-key")

def _auth(x_api_key: str):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/reindex")
def reindex_all(x_api_key: str = Header(...)):
    _auth(x_api_key)
    stats = index_dir("app/data/corpus", "laws")
    return {"status":"ok","indexed":stats}

@router.post("/update")
def update_and_index(payload: dict, x_api_key: str = Header(...)):
    _auth(x_api_key)
    sources = payload.get("sources", [])
    stats = run_update(sources, "app/data/corpus")
    return {"status":"ok","indexed":stats}
