from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(64), nullable=False)
    study_streak = Column(Integer, default=1)
    articles_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserToken(Base):
    __tablename__ = "user_tokens"

    token = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
