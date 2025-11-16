"""
API Auth – FI9_NAYEK v12.1
- Endpoint GET /api/auth/me utilisant get_current_user()
"""
from fastapi import APIRouter, Depends
from ..auth.supabase_auth import get_current_user, CurrentUser
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me", response_model=CurrentUser)
def get_me(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    logger.info("✅ Endpoint /api/auth/me appelé (Mode C)")
    return user