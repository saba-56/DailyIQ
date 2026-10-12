from sqlalchemy import Column, Integer, String, Text
from database.database import Base


class Affair(Base):
    __tablename__ = "affairs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    remember = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)

    # New field for daily quiz and historical practice
    published_at = Column(String(50), nullable=True)