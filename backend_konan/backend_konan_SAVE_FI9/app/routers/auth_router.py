# ============================================
# app/routers/auth_router.py — Mock pour tests
# ============================================
from fastapi import APIRouter, HTTPException, status, Depends

router = APIRouter(prefix="/auth", tags=["Auth (mock)"])

# /auth/login → renvoie 401 pour les tests
@router.post("/login")
async def login_mock(data: dict):
    email = data.get("email")
    password = data.get("password")
    if email and password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mock unauthorized")
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid payload")

# /auth/me → renvoie 403 si pas de token
@router.get("/me")
async def me_mock():
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Mock forbidden")

# Dépendance factice pour tests locaux
def get_current_user(token: str = Depends(lambda: None)):
    """Mock de dépendance pour FastAPI"""
    return {"email": "mock@konan.local"}
