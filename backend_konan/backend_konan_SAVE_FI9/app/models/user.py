import enum
from sqlalchemy import Column, Integer, String, Enum as PgEnum, DateTime
from sqlalchemy.sql import func
from app.database import Base

class PlanType(str, enum.Enum):
    FREE = "FREE"
    PRO = "PRO"
    LEGAL_PLUS = "LEGAL_PLUS"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    plan = Column(PgEnum(PlanType, name="plan_type"), default=PlanType.FREE)
