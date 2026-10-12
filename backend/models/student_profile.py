from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.database import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, unique=True)
    profile_name = Column(String(100), default="Student")
    degree = Column(String(100), default="B.Tech")
    branch = Column(String(100), default="CSE")
    study_year = Column(String(100), default="4th year")
    preferred_skills = Column(Text, default="Python, Java, SQL, Web Development")
    preferred_location = Column(String(150), default="India")
