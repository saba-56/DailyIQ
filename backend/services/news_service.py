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
# 2. NOISE & IMPORTANCE FILTER
# --------------------------------------------------

NOISE_KEYWORDS = [
    # Entertainment / Celebrity Gossip / Film Marketing
    "trailer out", "trailer release", "teaser out", "teaser drops", "box office", "box-office",
    "movie review", "film review", "ott release", "spotted at", "airport look", "red carpet",
    "paparazzi", "dating rumors", "dating rumour", "wedding photos", "wedding pictures",
    "bollywood gossip", "hollywood gossip", "bigg boss", "reality show", "outfit look",
    "samay raina", "influencer", "reels star", "viral video", "tiktok", "instagram video",
    
    # Horoscopes / Astrology / Superstition
    "horoscope", "zodiac", "astrology", "rashifal", "kundali", "tarot reading",
    
    # Sensational viral drama & clickbait
    "internet stunned", "netizens react", "jaw-dropping", "breaks the internet",
    "fans go wild", "twitter reacts", "x reacts", "fans divided",
    
    # Petty / local non-policy crimes
    "chain snatching", "drunk driving", "brawl in bar", "stole phone", "stole bike", "posed as teen"
]

HIGH_VALUE_INDICATORS = [
    # Law, Judiciary & Constitutional Governance
    "supreme court", "high court", "constitution", "verdict", "bench", "cji",
    "parliament", "lok sabha", "rajya sabha", "cabinet", "ordinance", "legislation",
    "election commission", "cag", "union ministry", "central government",
    
    # Economy, Finance, Trade & Monetary Policy
    "rbi", "reserve bank", "repo rate", "inflation", "cpi", "wpi", "gdp", "growth rate",
    "fiscal deficit", "sebi", "sensex", "nifty", "trade deficit", "rupee", "tax", "gst",
    
    # Science, Space, Defense & Frontier Tech
    "isro", "nasa", "drdo", "satellite", "gaganyaan", "chandrayaan", "space mission",
    "artificial intelligence", "semiconductor", "quantum computing", "clinical trial",
    "vaccine", "who", "public health", "mortality", "tb decline",
    
    # Geopolitics & Foreign Affairs
    "summit", "bilateral", "treaty", "united nations", "un security council",
    "brics", "g20", "quad", "asean", "diplomacy", "foreign policy", "ceasefire",
    "sanctions", "peace talks", "international relations",
    
    # Environment & Climate Regulations
    "air quality", "aqi", "grap", "pollution", "renewable energy", "climate change",
    "green hydrogen", "cop29", "cop30", "forest conservation",
    
    # Major Sports Milestones (Championships, Medals, World Cups)
    "world cup", "olympics", "asian games", "commonwealth", "championship",
    "border-gavaskar", "test series", "gold medal", "world title", "grand slam"
]


def is_article_noise(title: str, description: str = "") -> bool:
    """
    Returns True if an article matches clear noise patterns (celebrity gossip,
    movie trailers, horoscopes, influencer drama), UNLESS it contains high-value
    constitutional, economic, or scientific indicators.
    """
    text = (title + " " + (description or "")).lower()

    # Always keep high-value national/scientific/economic news
    if any(indicator in text for indicator in HIGH_VALUE_INDICATORS):
        return False

    # Filter out clear noise
    if any(noise in text for noise in NOISE_KEYWORDS):
        return True

    return False


# --------------------------------------------------
# 3. DETECT NEWS CATEGORY
# --------------------------------------------------

def get_category(title, description):
    text = (title + " " + description).lower()

    categories = {
        "Technology": [
            "technology", "artificial intelligence", " ai ",
            "software", "computer", "google", "microsoft",
            "apple", "cyber", "startup", "robot", "semiconductor",
            "microchip", "quantum", "telecom", "5g", "6g"
        ],

        "Economy": [
            "economy", "economic", "inflation", "market",
            "business", "bank", "rupee", "finance", "stock",
            "investment", "gdp", "tax", "rbi", "repo rate",
            "sensex", "nifty", "trade", "export", "import", "sebi"
        ],

        "Sports": [
            "cricket", "football", "tennis", "sports",
            "olympics", "match", "player", "tournament",
            "world cup", "championship", "batting", "bowling",
            "wicket", "innings", "t20", "odi", "bcci", "icc",
            "border-gavaskar", "badminton", "hockey"
        ],

        "Science": [
            "science", "space", "nasa", "isro",
            "research", "scientist", "astronomy",
            "satellite", "physics", "biology", "sun", "solar",
            "planet", "moon", "galaxy", "universe", "earthquake",
            "volcano", "discovery", "gaganyaan", "clinical trial",
            "vaccine", "health", "mortality"
        ],

        "Education": [
            "education", "school", "university",
            "college", "student", "exam", "academic",
            "scholarship", "teacher", "ugc", "aicte", "nep"
        ],

        "Environment": [
            "climate", "environment", "pollution",
            "weather", "forest", "wildlife",
            "global warming", "carbon emissions", "aqi",
            "air quality", "caqm", "grap", "renewable"
        ],

        "Politics": [
            "government", "minister", "parliament",
            "election", "political", "president",
            "prime minister", "lok sabha", "rajya sabha",
            "supreme court", "high court", "judiciary",
            "verdict", "cabinet", "ordinance", "bill"
        ]
    }

    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category

    return "National"


# --------------------------------------------------
# 4. FETCH NEWS (GNEWS + LIVE RSS)
# --------------------------------------------------

def fetch_rss_news():
    """
    Fetches real-time headlines from Google News India RSS feed.
    No API keys, no daily rate limits, and updates continuously 24/7.
    """
    import urllib.request
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime

    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    articles = []

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            xml_data = resp.read()

        root = ET.fromstring(xml_data)
        channel = root.find("channel")
        if channel is None:
            return []

        for item in channel.findall("item"):
            title_elem = item.find("title")
            link_elem = item.find("link")
            pub_date_elem = item.find("pubDate")
            desc_elem = item.find("description")
            source_elem = item.find("source")

            title = (title_elem.text or "").strip() if title_elem is not None else ""
            link = (link_elem.text or "").strip() if link_elem is not None else ""
            desc = (desc_elem.text or "").strip() if desc_elem is not None else ""
            source_name = source_elem.text if source_elem is not None else "Google News"

            # Strip HTML tags from description if present
            clean_desc = re.sub(r"<[^>]+>", "", desc).strip() if desc else title

            published_at = None
            if pub_date_elem is not None and pub_date_elem.text:
                try:
                    dt = parsedate_to_datetime(pub_date_elem.text)
                    published_at = dt.astimezone(ZoneInfo("Asia/Kolkata")).isoformat()
                except Exception:
                    published_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
            else:
                published_at = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()

            if title:
                articles.append({
                    "title": title,
                    "description": clean_desc,
                    "url": link,
                    "publishedAt": published_at,
                    "source": {"name": source_name}
                })

    except Exception as exc:
        print("Live RSS fetch notice:", exc)

    return articles


def fetch_news():
    """
    Combines GNews top headlines with real-time RSS updates so news refreshes
    seamlessly throughout the day (morning, afternoon, and evening).
    """
    combined_articles = []
    seen_urls = set()

    # 1. Fetch from GNews if API key is provided
    if GNEWS_API_KEY:
        url = "https://gnews.io/api/v4/top-headlines"
        params = {
            "apikey": GNEWS_API_KEY,
            "lang": "en",
            "country": "in",
            "max": 20
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for a in data.get("articles", []):
                    u = a.get("url")
                    if u and u not in seen_urls:
                        seen_urls.add(u)
                        combined_articles.append(a)
        except Exception as exc:
            print("GNews request notice:", exc)

    # 2. Fetch live RSS updates to capture breaking news throughout the day
    rss_articles = fetch_rss_news()
    for a in rss_articles:
        u = a.get("url")
        if u and u not in seen_urls:
            seen_urls.add(u)
            combined_articles.append(a)

    return combined_articles


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


def prune_noise_affairs(db):
    """
    Scans the database and removes low-value noise articles (celebrity gossip,
    movie trailers, horoscopes, influencer drama) while safely cleaning references.
    """
    from models.bookmark import Bookmark
    from models.quiz_question import QuizQuestion

    rows = db.query(Affair).all()
    removed = 0

    for affair in rows:
        if is_article_noise(affair.title, affair.summary):
            try:
                db.query(Bookmark).filter(Bookmark.affair_id == affair.id).delete()
                db.query(QuizQuestion).filter(QuizQuestion.affair_id == affair.id).delete()
                db.delete(affair)
                removed += 1
            except Exception as exc:
                print(f"Error removing noise affair {affair.id}: {exc}")

    if removed > 0:
        db.commit()

    return removed


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
    skipped_noise = 0

    try:
        # Load recent articles to check against for same-story duplicates
        recent_affairs = (
            db.query(Affair)
            .order_by(Affair.id.desc())
            .limit(150)
            .all()
        )

        for article in articles:
            source = article.get("source") or {}

            source_url = article.get("url", "")
            title = (article.get("title") or "").strip()
            description = (article.get("description") or "").strip()

            if not title:
                continue

            # Skip low-value noise (celebrity gossip, movie trailers, horoscopes, influencer drama)
            # while strictly preserving high-value national, economic, scientific, educational news
            if is_article_noise(title, description):
                skipped_noise += 1
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

        # Run prune to clean up any pre-existing duplicates and noise in DB
        pruned_dupes = prune_duplicate_affairs(db)
        pruned_noise = prune_noise_affairs(db)

    except Exception:
        db.rollback()
        raise

    return {
        "message": "News import completed!",
        "total_fetched": len(articles) if isinstance(articles, list) else 0,
        "added": added,
        "updated": updated,
        "skipped_duplicates": skipped_duplicates,
        "skipped_noise": skipped_noise,
        "pruned_duplicates": pruned_dupes,
        "pruned_noise": pruned_noise
    }

