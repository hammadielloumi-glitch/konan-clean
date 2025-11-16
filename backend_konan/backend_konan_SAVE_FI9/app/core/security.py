import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=True)

SECRET_KEY = os.getenv("JWT_SECRET", "change-me")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(
    subject: str | int,
    expires_minutes: Optional[int] = None,
    claims: Optional[Dict[str, Any]] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp()),
    }
    if claims:
        payload.update(claims)

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, Any]:
    token = credentials.credentials
    try:
        data = decode_token(token)
        sub = data.get("sub")
        if not isinstance(sub, str):
            raise JWTError("Subject must be a string.")
        return data
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
