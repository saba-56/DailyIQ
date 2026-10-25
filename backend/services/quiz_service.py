
import json
import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from models.affair import Affair
from models.quiz_question import QuizQuestion

load_dotenv()

IST = ZoneInfo("Asia/Kolkata")
GEMINI_MODEL = "gemini-3.5-flash-lite"


def get_gemini_client():
    """Create a Gemini client only when an API call is needed."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing from backend/.env")
    return genai.Client(api_key=api_key)


def get_published_date(article):
    """Return the article publication date in Indian Standard Time."""
    value = article.published_at

    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            value.strip().replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=IST)

        return parsed.astimezone(IST).date()

    except (ValueError, TypeError, AttributeError):
        return None


def generate_mcq(article):
    """
    Generate one comprehension-based MCQ from a stored article.
    Returns None if the response cannot be safely validated.
    """
    client = get_gemini_client()

    prompt = f"""
You are creating a factual current-affairs quiz for students.

Use ONLY the information in the article below.
Do not invent facts or use outside knowledge.

TITLE:
{article.title}

SUMMARY:
{article.summary}

KEY POINT TO REMEMBER:
{article.remember or "Not provided"}

Return exactly one MCQ as a JSON object with these fields:
- question: a clear question testing understanding of the article
- options: an object with keys A, B, C, D
- correct_option: exactly one of A, B, C, D
- explanation: a short explanation supported by the article
- difficulty: easy, medium, or hard
- topic: a short topic label

Rules:
1. Ask about a meaningful fact, event, purpose, outcome, or concept.
2. Do not ask which headline matches the article.
3. Give exactly four distinct, plausible options.
4. Exactly one option must be correct based on the article.
5. Keep all options and the explanation grounded in the supplied text.
6. Return valid JSON only, without Markdown fences.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.3,
        },
    )

    if not response.text:
        return None

    try:
        data = json.loads(response.text)
    except (json.JSONDecodeError, TypeError):
        return None

    question_text = data.get("question")
    options = data.get("options")
    correct = data.get("correct_option")
    explanation = data.get("explanation")
    difficulty = data.get("difficulty", "medium")
    topic = data.get("topic") or article.category or "Current Affairs"

    if not isinstance(question_text, str) or not question_text.strip():
        return None

    if not isinstance(options, dict):
        return None

    keys = ["A", "B", "C", "D"]
    if any(
        not isinstance(options.get(key), str)
        or not options[key].strip()
        for key in keys
    ):
        return None

    normalized_options = {
        key: options[key].strip()
        for key in keys
    }

    # Reject repeated options.
    if len({
        value.casefold()
        for value in normalized_options.values()
    }) != 4:
        return None

    if correct not in keys:
        return None

    if not isinstance(explanation, str) or not explanation.strip():
        return None

    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"

    return {
        "question": question_text.strip(),
        "options": normalized_options,
        "correct_option": correct,
        "explanation": explanation.strip(),
        "difficulty": difficulty,
        "topic": str(topic)[:100],
    }


def generate_for_articles(
    db: Session,
    articles,
    quiz_type: str,
    distractor_articles=None,
):
    """
    Generate article-based MCQs with Gemini.
    Reuse existing questions to keep attempts consistent.
    """
    usable = [
        article for article in articles
        if article.title
        and article.summary
        and article.title.strip()
        and article.summary.strip()
    ]

    created = 0

    for article in usable:
        already_exists = (
            db.query(QuizQuestion.id)
            .filter(
                QuizQuestion.affair_id == article.id,
                QuizQuestion.quiz_type == quiz_type,
            )
            .first()
        )

        if already_exists:
            continue

        try:
            mcq = generate_mcq(article)

            # Do not save malformed or invalid model responses.
            if not mcq:
                print(
                    f"Skipping article {article.id}: "
                    "Gemini returned an invalid MCQ."
                )
                continue

            choices = mcq["options"]

            question = QuizQuestion(
                affair_id=article.id,
                question=mcq["question"],
                option_a=choices["A"],
                option_b=choices["B"],
                option_c=choices["C"],
                option_d=choices["D"],
                correct_option=mcq["correct_option"],
                explanation=mcq["explanation"],
                topic=mcq["topic"],
                difficulty=mcq["difficulty"],
                quiz_type=quiz_type,
                created_at=datetime.now(IST).isoformat(),
            )

            db.add(question)
            db.flush()
            created += 1

        except Exception as exc:
            # A failed article should not prevent later articles
            # from being processed.
            db.rollback()
            print(
                f"Gemini quiz generation failed for article "
                f"{article.id}: {type(exc).__name__}: {exc}"
            )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return created


def generate_practice_questions(
    db: Session,
    limit: int = 50,
):
    """Generate practice questions from recent stored articles."""
    articles = (
        db.query(Affair)
        .order_by(Affair.id.desc())
        .limit(limit)
        .all()
    )

    created = generate_for_articles(
        db=db,
        articles=articles,
        quiz_type="practice",
    )

    return {
        "created": created,
    }


def generate_today_questions(
    db: Session,
    limit: int = 10,
):
    """Generate today's quiz using articles published today."""
    today = datetime.now(IST).date()

    all_articles = (
        db.query(Affair)
        .order_by(Affair.id.desc())
        .all()
    )

    todays_articles = [
        article
        for article in all_articles
        if get_published_date(article) == today
        and article.title
        and article.summary
    ][:limit]

    # If today has few articles, fall back to the most recent articles
    if len(todays_articles) < 3:
        todays_articles = [
            article
            for article in all_articles
            if article.title and article.summary
        ][:limit]

    created = generate_for_articles(
        db=db,
        articles=todays_articles,
        quiz_type="today",
    )

    return {
        "date": today.isoformat(),
        "eligible_articles": len(todays_articles),
        "created": created,
    }
