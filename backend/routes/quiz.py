
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.database import get_db
from models.quiz_question import QuizQuestion
from models.affair import Affair
from services.quiz_service import (
    generate_practice_questions,
    generate_today_questions,
)
from services.quiz_service import generate_practice_questions
router = APIRouter(prefix="/quiz", tags=["quiz"])

IST = ZoneInfo("Asia/Kolkata")


class QuizAnswer(BaseModel):
    question_id: int
    selected_option: str = Field(pattern="^[ABCDabcd]$")


class QuizSubmission(BaseModel):
    answers: list[QuizAnswer]


def question_for_student(question):
    return {
        "id": question.id,
        "question": question.question,
        "options": {
            "A": question.option_a,
            "B": question.option_b,
            "C": question.option_c,
            "D": question.option_d,
        },
        "topic": question.topic,
        "difficulty": question.difficulty,
        "source_url": (
            question.affair.source_url
            if question.affair else None
        ),
        "source_title": (
            question.affair.title
            if question.affair else None
        ),
    }


@router.get("/today")
def get_today_quiz(db: Session = Depends(get_db)):
    today = datetime.now(IST).date().isoformat()

    questions = (
        db.query(QuizQuestion)
        .filter(
            QuizQuestion.quiz_type == "today",
            QuizQuestion.created_at.like(f"{today}%")
        )
        .order_by(QuizQuestion.id.asc())
        .limit(10)
        .all()
    )

    # Auto-generate with Gemini if none exist yet for today
    if not questions:
        try:
            generate_today_questions(db, limit=5)
            questions = (
                db.query(QuizQuestion)
                .filter(
                    QuizQuestion.quiz_type == "today",
                    QuizQuestion.created_at.like(f"{today}%")
                )
                .order_by(QuizQuestion.id.asc())
                .limit(10)
                .all()
            )
        except Exception as exc:
            print("Auto-generate today quiz error:", exc)

    return {
        "date": today,
        "total_questions": len(questions),
        "questions": [
            question_for_student(q) for q in questions
        ],
        "message": (
            "No questions available yet."
            if not questions else "Today's quiz is ready."
        )
    }


@router.get("/practice")
def get_practice_quiz(
    topic: str | None = None,
    difficulty: str | None = Query(
        default=None,
        pattern="^(easy|medium|hard)$"
    ),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    query = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_type == "practice"
    )

    if topic:
        query = query.filter(QuizQuestion.topic == topic)

    if difficulty:
        query = query.filter(
            QuizQuestion.difficulty == difficulty
        )

    questions = (
        query.order_by(QuizQuestion.id.desc())
        .limit(limit)
        .all()
    )

    # Auto-generate practice questions if pool is empty
    if not questions and not topic and not difficulty:
        try:
            generate_practice_questions(db, limit=5)
            questions = (
                query.order_by(QuizQuestion.id.desc())
                .limit(limit)
                .all()
            )
        except Exception as exc:
            print("Auto-generate practice quiz error:", exc)

    return {
        "total_questions": len(questions),
        "questions": [
            question_for_student(q) for q in questions
        ]
    }


@router.post("/submit")
def submit_quiz(
    submission: QuizSubmission,
    db: Session = Depends(get_db)
):
    if not submission.answers:
        raise HTTPException(
            status_code=400,
            detail="Submit at least one answer."
        )

    question_ids = [
        answer.question_id for answer in submission.answers
    ]

    if len(question_ids) != len(set(question_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate question IDs are not allowed."
        )

    questions = (
        db.query(QuizQuestion)
        .filter(QuizQuestion.id.in_(question_ids))
        .all()
    )

    question_map = {q.id: q for q in questions}

    if len(question_map) != len(question_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more questions were not found."
        )

    results = []
    score = 0

    for answer in submission.answers:
        question = question_map[answer.question_id]
        selected = answer.selected_option.upper()
        correct = question.correct_option.upper()
        is_correct = selected == correct

        if is_correct:
            score += 1

        results.append({
            "question_id": question.id,
            "selected_option": selected,
            "correct_option": correct,
            "is_correct": is_correct,
            "explanation": question.explanation,
        })

    return {
        "total_questions": len(submission.answers),
        "correct_answers": score,
        "incorrect_answers": len(submission.answers) - score,
        "score_percentage": round(
            score / len(submission.answers) * 100, 2
        ),
        "results": results,
    }
@router.post("/generate-practice")
def generate_practice(db: Session = Depends(get_db)):
    try:
        return generate_practice_questions(db)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Question generation failed: {str(exc)}",
        )

@router.post("/generate-today")
def generate_today(db: Session = Depends(get_db)):
    try:
        return generate_today_questions(db)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Today's quiz generation failed: {str(exc)}",
        )
 
@router.get("/debug-today")
def debug_today(db: Session = Depends(get_db)):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from services.quiz_service import get_published_date

    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    articles = (
        db.query(Affair)
        .order_by(Affair.id.desc())
        .limit(15)
        .all()
    )

    return {
        "today_ist": today.isoformat(),
        "total_articles": len(articles),
        "articles": [
            {
                "title": article.title,
                "published_at": article.published_at,
                "parsed_date_ist": (
                    get_published_date(article).isoformat()
                    if get_published_date(article)
                    else None
                ),
            }
            for article in articles
        ],
    }
       