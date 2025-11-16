"""
Auth Supabase (Mode C) – FI9_NAYEK v12.1
- Modèle CurrentUser
- Dépendance get_current_user() basée sur le JWT Supabase HS256
"""
from typing import Optional, Dict
from fastapi import Header, HTTPException, status
from pydantic import BaseModel
from ..security.supabase_jwt import decode_supabase_jwt, extract_token_from_header


class CurrentUser(BaseModel):
    id: str
    email: Optional[str] = None
    role: Optional[str] = None
    raw_payload: Dict


def get_current_user(authorization: Optional[str] = Header(None)) -> CurrentUser:
    """
    Dépendance FastAPI pour récupérer l'utilisateur courant à partir du JWT Supabase.
    - Lit l'en-tête Authorization: Bearer <token>
    - Décode et vérifie le JWT
    - Mappe sub -> id, email -> email, role -> role (ou app_metadata.role si présent)
    - Renvoie CurrentUser ou erreurs FI9 standardisées (401/403)
    """
    token = extract_token_from_header(authorization)
    if not token:
        error_msg = "FI9-401: Authorization manquante ou invalide"
        exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg,
        )
        raise exc

    ok, payload, err = decode_supabase_jwt(token)
    if not ok or not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=err or "FI9-401: JWT invalide",
        )

    # Récupération des champs
    sub = payload.get("sub")
    email = payload.get("email") or payload.get("user_metadata", {}).get("email")
    role = payload.get("role") or payload.get("app_metadata", {}).get("role")

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FI9-403: Payload JWT incomplet (sub manquant)",
        )

    return CurrentUser(id=str(sub), email=email, role=role, raw_payload=payload)