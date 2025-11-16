import logging
import os
from copy import deepcopy

from fastapi import HTTPException, status

from app.models.user import User, PlanType

logger = logging.getLogger(__name__)

FAKE_TEST_USER = User(
    id=0,
    email="test-temp@konan.ai",
    full_name="Mode Test Sans Auth",
    hashed_password="",
    plan=PlanType.FREE,
)


def optional_user():
    """
    Retourne un utilisateur factice lorsque le mode test est activé.
    Lève une erreur si le bypass n'est pas autorisé.
    """
    if os.getenv("KONAN_TEST_MODE", "0") == "1":
        logger.warning("MODE TEST : Auth bypass - renvoi de l'utilisateur factice")
        return deepcopy(FAKE_TEST_USER)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Auth bypass disabled",
    )

