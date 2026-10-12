from sqlalchemy import Column, Integer, String, Text,Boolean
from database.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=True)
    deadline = Column(String(100), nullable=True)
    link = Column(String(500), nullable=True)
    degree = Column(String(100), nullable=True)
    branch = Column(String(100), nullable=True)
    study_year = Column(String(100), nullable=True)
    required_skills = Column(Text, nullable=True)
    location = Column(String(150), nullable=True)

    # Source and verification details
    source_url = Column(String(500), nullable=True)
    verified = Column(Boolean, default=False, nullable=False)