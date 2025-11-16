from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, PlanType
from app.core.security import hash_password

router = APIRouter(tags=["Auth Seed"])


@router.post("/seed-test-user")
def seed_test_user(db: Session = Depends(get_db)):
    """
    Crée un utilisateur de test cohérent avec la suite de tests locale.
    Email : test@konan.ai
    Password : KING
    """
    email = "test@konan.ai"
    password = "KING"

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return {
            "status": "ok",
            "message": "Utilisateur déjà présent",
            "email": email,
        }

    new_user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name="Compte de Test",
        plan=PlanType.FREE,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "ok",
        "message": "Utilisateur de test créé",
        "email": new_user.email,
    }
