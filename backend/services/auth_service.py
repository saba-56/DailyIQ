import hashlib
import secrets
from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User, UserToken


def hash_password(password: str, salt: Optional[str] = None):
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()
    return hashed, salt


def verify_password(password: str, salt: str, hashed: str) -> bool:
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, hashed)


def create_token_for_user(db: Session, user_id: int) -> str:
    token = secrets.token_hex(32)
    user_token = UserToken(token=token, user_id=user_id)
    db.add(user_token)
    db.commit()
    return token


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    parts = authorization.strip().split(" ")
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
    else:
        token = authorization.strip()

    user_token = db.query(UserToken).filter(UserToken.token == token).first()
    if not user_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )

    user = db.query(User).filter(User.id == user_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
