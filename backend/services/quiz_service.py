
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from models.affair import Affair
from models.quiz_question import QuizQuestion

IST = ZoneInfo("Asia/Kolkata")


def get_published_date(article):
    """Return the article publication date in Indian Standard Time."""
    value = article.published_at

    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            value.strip().replace("Z", "+00:00")
        )

        # Treat timestamps without a timezone as IST.
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=IST)

        return parsed.astimezone(IST).date()

    except (ValueError, TypeError, AttributeError):
        return None


def generate_for_articles(
    db: Session,
    articles,
    quiz_type: str,
    distractor_articles=None,
):
    """
    Generate headline-based MCQs from stored news articles.
    Reuse existing questions to keep attempts consistent.
    """
    usable = [
        article
        for article in articles
        if article.title and article.summary
        and article.title.strip()
    ]

    pool = (
        distractor_articles
        if distractor_articles is not None
        else usable
    )

    # Collect distinct real headlines for answer options.
    titles = list(dict.fromkeys(
        article.title.strip()
        for article in pool
        if article.title and article.title.strip()
    ))

    if len(titles) < 4:
        return 0

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

        correct_title = article.title.strip()

        other_titles = [
            title
            for title in titles
            if title != correct_title
        ]

        if len(other_titles) < 3:
            continue

        # Put the correct answer in option A.
        choices = [correct_title] + other_titles[:3]

        question = QuizQuestion(
            affair_id=article.id,
            question="Which headline matches this news article?",
            option_a=choices[0],
            option_b=choices[1],
            option_c=choices[2],
            option_d=choices[3],
            correct_option="A",
            explanation=(
                f"Article: {article.title}\n"
                f"Summary: {article.summary}\n"
                f"Key point: {article.remember or article.summary}"
            ),
            topic=article.category,
            difficulty="easy",
            quiz_type=quiz_type,
            created_at=datetime.now(IST).isoformat(),
        )

        db.add(question)
        created += 1

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

    # Load articles once so older headlines can be used as options.
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

    # Older articles provide distractors, not today's questions.
    distractor_articles = [
        article
        for article in all_articles
        if article.title and article.title.strip()
    ]

    created = generate_for_articles(
        db=db,
        articles=todays_articles,
        quiz_type="today",
        distractor_articles=distractor_articles,
    )

    return {
        "date": today.isoformat(),
        "eligible_articles": len(todays_articles),
        "created": created,
    }