"""
Sécurité Supabase JWT (Mode C) – FI9_NAYEK v12.1
- Décodage JWT HS256 en utilisant la variable d'environnement KONAN_SUPABASE_JWT_SECRET
- Validation optionnelle exp/nbf
- Extraction du token depuis l'en-tête Authorization: Bearer <token>
"""
import os
import json
import time
import hmac
import hashlib
from typing import Optional, Tuple, Dict


class FI9Error(Exception):
    """Erreur générique FI9 pour signaler les échecs de sécurité."""


def base64_urlsafe_decode(data: str) -> bytes:
    """Décode une chaîne base64url en bytes."""
    import base64
    return base64.urlsafe_b64decode(data.encode("utf-8"))


def _base64url_decode(data: str) -> bytes:
    """Ajoute le padding manquant puis décode en base64url."""
    rem = len(data) % 4
    if rem:
        data += "=" * (4 - rem)
    return base64_urlsafe_decode(data)


def decode_supabase_jwt(token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Décode et vérifie un JWT Supabase signé en HS256.
    Retourne (ok, payload_dict, error_message).

    - ok: True si signature valide et payload déchiffré
    - payload_dict: dict du payload JWT si ok, sinon None
    - error_message: message FI9 en cas d'erreur
    """
    try:
        if not token or token.count(".") != 2:
            return False, None, "FI9-400: Token JWT mal formé"

        secret = os.getenv("KONAN_SUPABASE_JWT_SECRET", "")
        if not secret:
            return False, None, "FI9-500: Secret JWT non configuré"

        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

        # Vérifier signature HS256: HMAC-SHA256(signing_input, secret)
        import base64
        expected_sig = hmac.new(
            key=secret.encode("utf-8"),
            msg=signing_input,
            digestmod=hashlib.sha256,
        ).digest()
        try:
            provided_sig = base64.urlsafe_b64decode(signature_b64 + "==")
        except Exception:
            return False, None, "FI9-400: Signature JWT invalide"

        if not hmac.compare_digest(expected_sig, provided_sig):
            return False, None, "FI9-401: Authorization manquante ou invalide"

        # Décoder header & payload
        try:
            header_json = base64.urlsafe_b64decode(header_b64 + "==").decode("utf-8")
            payload_json = base64.urlsafe_b64decode(payload_b64 + "==").decode("utf-8")
            header = json.loads(header_json)
            payload = json.loads(payload_json)
        except Exception:
            return False, None, "FI9-400: Payload JWT illisible"

        # Vérifier alg
        if header.get("alg") != "HS256":
            return False, None, "FI9-400: Algorithme JWT non supporté"

        # Validations exp/nbf (optionnelles)
        now = int(time.time())
        exp = payload.get("exp")
        nbf = payload.get("nbf")
        if exp is not None and isinstance(exp, int) and now >= exp:
            return False, None, "FI9-401: Authorization manquante ou invalide"
        if nbf is not None and isinstance(nbf, int) and now < nbf:
            return False, None, "FI9-401: Authorization manquante ou invalide"

        return True, payload, None
    except Exception as e:
        return False, None, f"FI9-500: Erreur interne JWT ({str(e)})"


def extract_token_from_header(header_value: Optional[str]) -> Optional[str]:
    """
    Extrait le token depuis une chaîne d'en-tête Authorization.
    Exemple: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if not header_value:
        return None
    parts = header_value.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None