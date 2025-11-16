from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, PlanType
from app.schemas.user_schemas import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "plan": user.plan.value}

@router.get("/me", response_model=UserResponse)
def me(db: Session = Depends(get_db)):
    return db.query(User).first()

@router.get("/plans")
def list_plans():
    return [
        {"name": "Free", "price": "0 TND", "limit": "10 messages/jour"},
        {"name": "Pro", "price": "25 TND/mois", "limit": "illimité"},
        {"name": "Legal+", "price": "70 TND/mois", "limit": "priorité IA + consultation humaine"},
    ]
