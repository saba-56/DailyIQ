
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.database import Base
from sqlalchemy.orm import relationship

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    affair = relationship("Affair")

    id = Column(Integer, primary_key=True, index=True)

    # Link the question to its source news article.
    affair_id = Column(
        Integer,
        ForeignKey("affairs.id"),
        nullable=False,
        index=True
    )

    question = Column(Text, nullable=False)

    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500), nullable=False)
    option_d = Column(String(500), nullable=False)

    # Store A, B, C, or D.
    correct_option = Column(String(1), nullable=False)

    explanation = Column(Text, nullable=False)

    topic = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=False, default="medium")

    # "today" for daily quizzes; "practice" for the question bank.
    quiz_type = Column(String(20), nullable=False, default="practice")

    created_at = Column(String(50), nullable=True)