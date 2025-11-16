from pydantic import BaseModel, EmailStr
from enum import Enum

class PlanType(str, Enum):
    FREE = "Free"
    PRO = "Pro"
    LEGAL_PLUS = "Legal+"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    plan: PlanType
    class Config:
        orm_mode = True
