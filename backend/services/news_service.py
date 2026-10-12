import os
import json
import requests

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
# 6. IMPORT NEWS INTO THE DATABASE
# --------------------------------------------------

def import_news_to_database(db):
    articles = fetch_news()

    if isinstance(articles, dict) and "gnews_error" in articles:
        return articles

    added = 0
    updated = 0

    try:
        for article in articles[:10]:
            source = article.get("source") or {}

            source_url = article.get("url", "")
            title = article.get("title", "")
            description = article.get("description", "")

            original_published_at = article.get(
                "publishedAt", ""
            )

            published_at = normalize_published_at(
                original_published_at
            )

            # Find an existing article by its source URL.
            existing = None

            if source_url:
                existing = db.query(Affair).filter(
                    Affair.source_url == source_url
                ).first()

            if existing:
                # Update the existing article.
                existing.category = get_category(
                    title, description
                )
                existing.title = title
                existing.summary = description

                existing.remember = json.dumps(
                    generate_remember(
                        title,
                        description,
                        published_at
                    )
                )

                existing.source = source.get(
                    "name", "Unknown"
                )
                existing.published_at = published_at

                updated += 1
                continue

            # Create a new article.
            affair = Affair(
                category=get_category(
                    title, description
                ),
                title=title,
                summary=description,
                remember=json.dumps(
                    generate_remember(
                        title,
                        description,
                        published_at
                    )
                ),
                source=source.get(
                    "name", "Unknown"
                ),
                source_url=source_url or None,
                published_at=published_at
            )

            db.add(affair)
            added += 1

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "News import completed!",
        "total_fetched": len(articles[:10]),
        "added": added,
        "updated": updated
 }

