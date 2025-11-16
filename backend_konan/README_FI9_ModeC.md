# README FI9 Mode C — Authentification Hybride Supabase (KONAN Backend)

Objectif: Implémenter une authentification hybride basée sur des JWT Supabase (HS256) côté FastAPI, avec:
- Décodage sécurisé des JWT Supabase
- Dépendance FastAPI `get_current_user`
- Webhook sécurisé de synchronisation utilisateur
- Endpoint `/api/auth/me`
- Sans casser la configuration existante (routers, CORS, middlewares…)
- Laisser les TODO DB/RLS pour une phase suivante

Stack cible: Python 3.11 / FastAPI  
Racine backend: `backend_konan`  
Code applicatif: `backend_konan/app`

Ce document fournit le design, les signatures, et des extraits/pseudocode commentés pour une implémentation rapide et sûre, conformément aux exigences FI9_NAYEK v12.1 (Mode C).

---

## 1) backend_konan/app/security/supabase_jwt.py

Responsabilités:
- Extraction du token depuis le header `Authorization: Bearer &lt;token&gt;`
- Décodage du JWT Supabase signé en HS256 avec `KONAN_SUPABASE_JWT_SECRET`
- Validations minimales (exp/nbf) — activables

Variables d’environnement:
- `KONAN_SUPABASE_JWT_SECRET`: secret Supabase (HS256). Obtenu depuis Supabase Settings > JWT Secret.

Signatures proposées:
```python
# backend_konan/app/security/supabase_jwt.py
from typing import Any, Dict, Optional
import os
from fastapi import HTTPException, status
import jwt  # PyJWT
from jwt import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError

FI9_UNAUTHORIZED = {"error_code": "FI9-401", "message": "Non authentifié"}
FI9_BAD_REQUEST = {"error_code": "FI9-400", "message": "Requête invalide"}

def extract_token_from_header(header: Optional[str]) -> str:
    """
    Extrait le token depuis un header Authorization de type 'Bearer &lt;token&gt;'.
    Lève 401 (FI9-401) si inexistant ou mal formé.
    """
    if not header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": "Header Authorization manquant"}
        )
    parts = header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": "Schéma d’authentification invalide"}
        )
    return parts[1]

def decode_supabase_jwt(token: str, *, verify_exp: bool = True, verify_nbf: bool = True) -> Dict[str, Any]:
    """
    Décode et vérifie un JWT Supabase (HS256) en utilisant KONAN_SUPABASE_JWT_SECRET.
    Valide exp/nbf si activés.
    Lève 401 (FI9-401) en cas d’échec.
    """
    secret = os.getenv("KONAN_SUPABASE_JWT_SECRET")
    if not secret:
        # Option: lever 500 si configuration manquante
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "FI9-500", "message": "Configuration manquante", "details": "KONAN_SUPABASE_JWT_SECRET"}
        )

    options = {
        "verify_exp": verify_exp,
        "verify_signature": True,
        # PyJWT n’a pas d’option 'verify_nbf' dédiée; elle est vérifiée par défaut si présente
    }

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options=options,
        )
        # Si besoin, valider 'nbf' manuellement:
        # - PyJWT vérifie nbf si présent; sinon ajouter contrôle spécifique.
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": "Token expiré"}
        )
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": "Signature invalide"}
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": f"Token invalide: {str(e)}"}
        )
    except Exception as e:
        # Garde-fou générique
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": f"Erreur de décodage JWT: {str(e)}"}
        )
```

Notes FI9:
- Ne pas logguer le token brut.
- Activer `verify_exp` par défaut; `nbf` est vérifié si présent.
- Retourner des erreurs standardisées (voir Section 7).

---

## 2) backend_konan/app/auth/supabase_auth.py

Responsabilités:
- Modèle `CurrentUser`: projection minimale sécurisée du JWT vers l’application
- Dépendance `get_current_user()` pour injection dans les routes protégées
- Standardisation des erreurs 401/403

Signatures proposées:
```python
# backend_konan/app/auth/supabase_auth.py
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, Request, status
from ..security.supabase_jwt import extract_token_from_header, decode_supabase_jwt

FI9_UNAUTHORIZED = {"error_code": "FI9-401", "message": "Non authentifié"}
FI9_FORBIDDEN = {"error_code": "FI9-403", "message": "Accès interdit"}

class CurrentUser(BaseModel):
    id: str
    email: EmailStr
    role: Optional[str] = None
    raw_payload: Dict[str, Any]

async def get_current_user(request: Request) -> CurrentUser:
    """
    - Extrait le header Authorization
    - Décode le JWT Supabase
    - Mappe sub/email/role vers CurrentUser
    - Lève 401/403 standardisées au besoin
    """
    auth_header = request.headers.get("Authorization")
    token = extract_token_from_header(auth_header)
    payload = decode_supabase_jwt(token)

    # Mapping depuis payload Supabase (exemples fréquents):
    # - sub: identifiant utilisateur
    # - email: email utilisateur
    # - role: champ direct ou dans app_metadata/custom claims
    uid = str(payload.get("sub") or "")
    email = payload.get("email")
    role = payload.get("role") or payload.get("app_metadata", {}).get("role")

    if not uid or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": "Claims requis manquants (sub/email)"}
        )

    # TODO (Phase RBAC): vérifier le role et lever 403 si non autorisé
    # if role not in {"user", "admin"}:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail={**FI9_FORBIDDEN, "details": "Rôle insuffisant"}
    #     )

    return CurrentUser(id=uid, email=email, role=role, raw_payload=payload)
```

Notes FI9:
- Les 401 renvoient FI9-401; 403 renvoient FI9-403.
- Ne pas coupler cette dépendance à la DB (pas de lecture DB à ce stade).

---

## 3) backend_konan/app/webhooks/sync_user.py

Responsabilités:
- Endpoint webhook sécurisé par HMAC pour synchroniser les changements utilisateur Supabase
- Vérification du header `X-Signature` (Base64 d’un HMAC SHA256 sur le body brut)
- Utilisation de `KONAN_SUPABASE_WEBHOOK_SECRET`
- Retour JSON `{status: "ok", payload}` si signature valide; 401 sinon

Variables d’environnement:
- `KONAN_SUPABASE_WEBHOOK_SECRET`: secret dédié aux webhooks.

Router et endpoint:
```python
# backend_konan/app/webhooks/sync_user.py
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
import os, hmac, hashlib, base64

router = APIRouter(prefix="/api/webhooks/supabase", tags=["webhooks"])

FI9_UNAUTHORIZED = {"error_code": "FI9-401", "message": "Non authentifié"}

def _compute_hmac_b64(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")

def _constant_time_equal(a: str, b: str) -> bool:
    # Utilise compare_digest (constant-time) pour éviter les attaques de timing
    return hmac.compare_digest(a, b)

@router.post("/user-sync")
async def supabase_user_sync(request: Request):
    """
    Vérifie la signature HMAC du payload brut avec KONAN_SUPABASE_WEBHOOK_SECRET.
    - Header attendu: X-Signature: base64(hmac_sha256(body))
    - Body: non modifié, ordre des clés préservé (utiliser request.body()).
    """
    secret = os.getenv("KONAN_SUPABASE_WEBHOOK_SECRET")
    if not secret:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": "FI9-500", "message": "Configuration manquante", "details": "KONAN_SUPABASE_WEBHOOK_SECRET"}
        )

    received_sig = request.headers.get("X-Signature")
    if not received_sig:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": "Signature manquante"}
        )

    body = await request.body()  # bytes bruts
    expected_sig = _compute_hmac_b64(secret, body)

    if not _constant_time_equal(received_sig, expected_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={**FI9_UNAUTHORIZED, "details": "Signature invalide"}
        )

    # TODO (Phase suivante): upsert utilisateur en DB, mapping des rôles, traçabilité des événements
    try:
        payload = await request.json()
    except Exception:
        payload = {"raw": body.decode("utf-8", errors="replace")}

    return {"status": "ok", "payload": payload}
```

Notes FI9:
- Toujours comparer en constant-time.
- Le body doit être lu en bytes bruts pour calculer l’HMAC avant tout parsing JSON.
- Conserver un design idempotent côté DB (phase suivante).

---

## 4) Mise à jour app/main.py (inclusion du router webhook)

Objectif: Inclure le router sans casser la config existante (CORS, autres routers, middlewares).

Extrait intégré (pseudocode):
```python
# backend_konan/app/main.py
from fastapi import FastAPI
# ... imports existants (CORS, autres routers)
from .webhooks.sync_user import router as supabase_user_sync_router

def create_app() -> FastAPI:
    app = FastAPI(title="KONAN API")
    # CORS existant
    # app.add_middleware(CORSMiddleware, ...)

    # Routers applicatifs existants
    # app.include_router(api_router)

    # Webhook Supabase (Mode C)
    app.include_router(supabase_user_sync_router)

    return app

app = create_app()
```

---

## 5) Mise à jour app/api/auth.py (GET /api/auth/me)

Objectif: exposer l’identité courante (projetée via CurrentUser).

Extrait intégré (pseudocode):
```python
# backend_konan/app/api/auth.py
from fastapi import APIRouter, Depends
from ..auth.supabase_auth import get_current_user, CurrentUser

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/me", response_model=CurrentUser)
async def read_me(current: CurrentUser = Depends(get_current_user)):
    return current
```

Notes:
- S’assurer que le routeur `auth` est bien inclus dans l’app principale (si déjà présent, ne pas dupliquer).
- `response_model=CurrentUser` documente et valide le schéma de sortie.

---

## 6) Variables d’environnement et sécurité

Requis:
- `KONAN_SUPABASE_JWT_SECRET`: secret HS256 du projet Supabase
- `KONAN_SUPABASE_WEBHOOK_SECRET`: secret pour signer et vérifier les webhooks

Bonnes pratiques:
- Charger les secrets via variables d’environnement (pas de hardcode).
- Ne pas logguer les tokens ou secrets.
- Utiliser `hmac.compare_digest` pour toute comparaison de signatures.
- Activer la vérification d’expiration `exp` par défaut, et respecter `nbf` si présent.
- Ajouter des tests unitaires sur:
  - extraction/erreurs du header Authorization
  - décodage JWT (signature invalide, expiré, claims manquants)
  - vérification HMAC (signature manquante/incorrecte)

---

## 7) Schémas d’erreurs FI9

Standard FI9 pour les réponses d’erreur JSON:
- FI9-401 (401 Unauthorized) — Non authentifié
- FI9-403 (403 Forbidden) — Accès interdit
- FI9-400 (400 Bad Request) — Requête invalide
- FI9-500 (500 Internal Server Error) — Erreur serveur / configuration manquante

Format JSON attendu:
```json
{
  "error_code": "FI9-401",
  "message": "Non authentifié",
  "details": "Token expiré"
}
```

Exemples d’utilisation:
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"error_code": "FI9-401", "message": "Non authentifié", "details": "Header Authorization manquant"}
)
```

---

## 8) TODOs RLS/DB (Phase suivante)

- Upsert utilisateur lors du webhook:
  - Mapper `sub` (id Supabase) → table `users.id_supabase`
  - Mapper `email` → `users.email`
  - Mapper `role` → `users.role` (depuis `payload["role"]` ou `payload["app_metadata"]["role"]`)
- Traiter les événements (user.created / user.updated) et conserver l’historique.
- RLS (Row Level Security):
  - Règles basées sur `id_supabase`
  - Politique lecture/écriture par rôle
- Idempotence: utiliser upsert par clé unique `id_supabase`.
- Traçabilité: journaliser l’horodatage, l’event type, et l’ID.

---

## 9) Tests manuels / Validation

1) Décodage JWT / `/api/auth/me`:
- Lancer l’API avec `KONAN_SUPABASE_JWT_SECRET` configuré.
- Requête:
```bash
curl -sS -H "Authorization: Bearer &lt;VOTRE_JWT_SUPABASE&gt;" http://localhost:8000/api/auth/me
```
- Réponse attendue:
```json
{
  "id": "uuid-supabase",
  "email": "user@example.com",
  "role": "user",
  "raw_payload": { "...": "..." }
}
```
- Cas d’erreur (token expiré/bad signature): 401 avec FI9-401.

2) Webhook user-sync:
- Calculer la signature HMAC SHA256 base64 sur le body brut:
```bash
BODY='{"type":"user.updated","data":{"id":"abc","email":"user@example.com"}}'
SIG=$(python - &lt;&lt;'PY'
import os, hmac, hashlib, base64, sys, json
secret = os.environ.get("KONAN_SUPABASE_WEBHOOK_SECRET","devsecret")
body = sys.stdin.read().encode("utf-8")
print(base64.b64encode(hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()).decode("utf-8"))
PY
 &lt;&lt;&lt; "$BODY")
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -H "X-Signature: $SIG" \
  -d "$BODY" \
  http://localhost:8000/api/webhooks/supabase/user-sync
```
- Réponse attendue:
```json
{"status": "ok", "payload": {"type":"user.updated","data":{"id":"abc","email":"user@example.com"}}}
```
- Signature absente/incorrecte: 401 avec FI9-401.

---

## 10) Intégration sans régression

- Ne pas modifier les middlewares et CORS existants.
- Ajouter simplement:
  - `from .webhooks.sync_user import router as supabase_user_sync_router`
  - `app.include_router(supabase_user_sync_router)`
- Conserver le routeur `auth` existant et y ajouter l’endpoint `/api/auth/me` (ou vérifier qu’il est présent).

---

## 11) Checklist d’implémentation rapide

- [ ] Créer `app/security/supabase_jwt.py` (extraits ci-dessus)
- [ ] Créer `app/auth/supabase_auth.py` avec `CurrentUser` et `get_current_user`
- [ ] Créer `app/webhooks/sync_user.py` et exposer `/api/webhooks/supabase/user-sync`
- [ ] Inclure le router webhook dans `app/main.py`
- [ ] Ajouter `GET /api/auth/me` dans `app/api/auth.py`
- [ ] Configurer `KONAN_SUPABASE_JWT_SECRET` et `KONAN_SUPABASE_WEBHOOK_SECRET`
- [ ] Tester `/api/auth/me` (Bearer) et le webhook (signature HMAC)

---

## 12) Notes complémentaires

- HS256 (secret partagé) facilite l’intégration mais impose une gestion stricte des secrets.
- En production, surveiller la rotation des secrets et les horloges (exp/nbf).
- Considérer une journalisation minimale et privacy-by-default (pas de PII en logs).
- Préparer la phase RLS/DB pour une cohérence complète (Mode C + base applicative).
