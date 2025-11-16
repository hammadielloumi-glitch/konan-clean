"""
Webhook de synchronisation utilisateur Supabase – FI9_NAYEK v12.1
- Route: POST /api/webhooks/supabase/user-sync
- Vérification HMAC SHA256 avec KONAN_SUPABASE_WEBHOOK_SECRET
- Header: X-Signature (base64)
- Réponse: {"status":"ok", "payload": <json payload>} si valide, 401 sinon
"""
import os
import hmac
import hashlib
import base64
from typing import Any, Dict
from fastapi import APIRouter, Request, HTTPException, status

router = APIRouter(prefix="/api/webhooks/supabase", tags=["webhooks"])


def _verify_signature(secret: str, body: bytes, provided_signature_b64: str) -> bool:
    try:
        expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
        provided = base64.b64decode(provided_signature_b64)
        return hmac.compare_digest(expected, provided)
    except Exception:
        return False


@router.post("/user-sync")
async def supabase_user_sync(request: Request) -> Dict[str, Any]:
    secret = os.getenv("KONAN_SUPABASE_WEBHOOK_SECRET", "")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FI9-500: Secret webhook non configuré",
        )

    raw = await request.body()
    signature = request.headers.get("X-Signature")
    if not signature or not _verify_signature(secret, raw, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="FI9-401: Signature webhook invalide",
        )

    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": raw.decode("utf-8", errors="ignore")}

    return {"status": "ok", "payload": payload}