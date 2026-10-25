import os
import json
import re
import requests
from difflib import SequenceMatcher

from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from models.affair import Affair


# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")


# --------------------------------------------------
# 2. DETECT NEWS CATEGORY
# --------------------------------------------------

def get_category(title, description):
    text = (title + " " + description).lower()

    categories = {
        "Technology": [
            "technology", "artificial intelligence", " ai ",
            "software", "computer", "google", "microsoft",
            "apple", "cyber", "startup", "robot", "semiconductor"
        ],

        "Economy": [
            "economy", "economic", "inflation", "market",
            "business", "bank", "rupee", "finance", "stock",
            "investment", "gdp", "tax"
        ],

        "Sports": [
            "cricket", "football", "tennis", "sports",
            "olympics", "match", "player", "tournament",
            "world cup", "championship"
        ],

        "Science": [
            "science", "space", "nasa", "isro",
            "research", "scientist", "astronomy",
            "satellite", "physics", "biology", "sun", "solar",
            "planet", "moon", "galaxy", "universe", "earthquake",
            "volcano", "discovery"
        ],

        "Education": [
            "education", "school", "university",
            "college", "student", "exam", "academic",
            "scholarship", "teacher"
        ],

        "Environment": [
            "climate", "environment", "pollution",
            "weather", "forest", "wildlife",
            "global warming", "carbon emissions"
        ],

        "Politics": [
            "government", "minister", "parliament",
            "election", "political", "president",
            "prime minister", "lok sabha", "rajya sabha"
        ]
    }

    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "National"


# --------------------------------------------------
# 3. FETCH NEWS FROM GNEWS
# --------------------------------------------------

def fetch_news():
    if not GNEWS_API_KEY:
        return {
            "gnews_error": "GNEWS_API_KEY is missing from the .env file."
        }

    url = "https://gnews.io/api/v4/top-headlines"

    params = {
        "apikey": GNEWS_API_KEY,
        "lang": "en",
        "country": "in",
        "max": 10
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "status_code": response.status_code,
                "gnews_error": response.text
            }

        data = response.json()
        return data.get("articles", [])

    except requests.RequestException as error:
        return {
            "gnews_error": str(error)
        }

    except ValueError:
        return {
            "gnews_error": "GNews returned an invalid JSON response."
        }


# --------------------------------------------------
# 4. GENERATE REMEMBER POINTS
# --------------------------------------------------

def generate_remember(title, description, published_at):
    points = []

    if title:
        points.append(f"Topic: {title}")

    if description:
        sentences = (
            description
            .replace("!", ".")
            .replace("?", ".")
            .split(".")
        )

        for sentence in sentences:
            sentence = sentence.strip()

            if sentence and len(sentence) > 20 and len(points) < 4:
                points.append(f"Key point: {sentence}")

    if published_at and len(points) < 4:
        points.append(f"Published: {published_at[:10]}")

    return points[:4]


# --------------------------------------------------
# 5. NORMALIZE PUBLICATION DATE TO IST
# --------------------------------------------------

def normalize_published_at(value):
    if not value:
        return None

    try:
        published = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        # Treat a timestamp without timezone information as UTC.
        if published.tzinfo is None:
            published = published.replace(
                tzinfo=ZoneInfo("UTC")
            )

        return published.astimezone(
            ZoneInfo("Asia/Kolkata")
        ).isoformat()

    except (ValueError, TypeError, AttributeError):
        return None


# --------------------------------------------------
# 6. STORY SIMILARITY & DEDUPLICATION
# --------------------------------------------------

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "is",
    "are", "was", "were", "be", "been", "by", "from", "with", "as", "about",
    "into", "through", "after", "over", "between", "out", "against", "during",
    "without", "before", "under", "around", "among", "says", "said", "new",
    "today", "first", "most", "day", "all", "its", "it", "his", "her", "their"
}


def extract_content_words(text: str) -> set[str]:
    """Extract lowercase words >= 3 characters excluding stop words."""
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {w for w in words if w not in STOP_WORDS and len(w) >= 3}


def is_same_story(title_a: str, title_b: str) -> bool:
    """
    Check if two titles cover the same breaking news event from different outlets.
    Example:
      'Gangster Himanshu Bhau, Wanted In India For Multiple Murders, Arrested In US' (NDTV)
      'Himanshu Bhau, India's most wanted gangster from Haryana, arrested in US' (India Today)
    """
    if not title_a or not title_b:
        return False

    a, b = title_a.strip().lower(), title_b.strip().lower()
    if a == b:
        return True

    # Do not merge different horoscope signs
    if "horoscope" in a and "horoscope" in b:
        return False

    # String similarity ratio check
    if SequenceMatcher(None, a, b).ratio() >= 0.72:
        return True

    # Shared keyword Jaccard similarity check
    words_a = extract_content_words(a)
    words_b = extract_content_words(b)
    if not words_a or not words_b:
        return False

    inter = words_a & words_b
    union = words_a | words_b
    jaccard = len(inter) / len(union) if union else 0

    return len(inter) >= 4 and jaccard >= 0.50


def prune_duplicate_affairs(db):
    """
    Scans the database and removes duplicate coverage of the same news story,
    keeping the most complete/recent article and preserving foreign key references.
    """
    from models.bookmark import Bookmark
    from models.quiz_question import QuizQuestion

    rows = (
        db.query(Affair)
        .order_by(Affair.published_at.desc(), Affair.id.desc())
        .all()
    )

    seen_ids = set()
    removed = 0

    for i, r1 in enumerate(rows):
        if r1.id in seen_ids:
            continue

        for r2 in rows[i + 1:]:
            if r2.id in seen_ids:
                continue

            d1 = (r1.published_at or "")[:10]
            d2 = (r2.published_at or "")[:10]
            if d1 and d2 and d1 != d2:
                continue

            if is_same_story(r1.title, r2.title):
                seen_ids.add(r2.id)
                try:
                    # Re-point any bookmarks or quiz questions to the kept article
                    db.query(Bookmark).filter(
                        Bookmark.affair_id == r2.id
                    ).update({Bookmark.affair_id: r1.id})

                    db.query(QuizQuestion).filter(
                        QuizQuestion.affair_id == r2.id
                    ).update({QuizQuestion.affair_id: r1.id})

                    db.delete(r2)
                    removed += 1
                except Exception as exc:
                    print(f"Error merging duplicate affair {r2.id}: {exc}")

    if removed > 0:
        db.commit()

    return removed


# --------------------------------------------------
# 7. IMPORT NEWS INTO THE DATABASE
# --------------------------------------------------

def import_news_to_database(db):
    articles = fetch_news()

    if isinstance(articles, dict) and "gnews_error" in articles:
        return articles

    added = 0
    updated = 0
    skipped_duplicates = 0

    try:
        # Load recent articles to check against for same-story duplicates
        recent_affairs = (
            db.query(Affair)
            .order_by(Affair.id.desc())
            .limit(60)
            .all()
        )

        for article in articles[:10]:
            source = article.get("source") or {}

            source_url = article.get("url", "")
            title = (article.get("title") or "").strip()
            description = (article.get("description") or "").strip()

            if not title:
                continue

            original_published_at = article.get("publishedAt", "")
            published_at = normalize_published_at(original_published_at)

            # 1. Find an existing article by exact source URL
            existing = None
            if source_url:
                existing = db.query(Affair).filter(
                    Affair.source_url == source_url
                ).first()

            if existing:
                existing.category = get_category(title, description)
                existing.title = title
                existing.summary = description
                existing.remember = json.dumps(
                    generate_remember(title, description, published_at)
                )
                existing.source = source.get("name", "Unknown")
                existing.published_at = published_at
                updated += 1
                continue

            # 2. Check if the exact same story is already in the database from another outlet
            article_date = (published_at or "")[:10]
            is_duplicate = False

            for prev in recent_affairs:
                prev_date = (prev.published_at or "")[:10]
                if article_date and prev_date and article_date != prev_date:
                    continue

                if is_same_story(title, prev.title):
                    is_duplicate = True
                    break

            if is_duplicate:
                skipped_duplicates += 1
                continue

            # 3. Create a new unique article
            affair = Affair(
                category=get_category(title, description),
                title=title,
                summary=description,
                remember=json.dumps(
                    generate_remember(title, description, published_at)
                ),
                source=source.get("name", "Unknown"),
                source_url=source_url or None,
                published_at=published_at
            )

            db.add(affair)
            db.flush()
            recent_affairs.insert(0, affair)
            added += 1

        db.commit()

        # Run prune to clean up any pre-existing duplicates in DB
        pruned = prune_duplicate_affairs(db)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "News import completed!",
        "total_fetched": len(articles[:10]),
        "added": added,
        "updated": updated,
        "skipped_duplicates": skipped_duplicates,
        "pruned_duplicates": pruned
    }

