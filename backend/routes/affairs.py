import json

from fastapi import APIRouter, Depends,Query, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.affair import Affair
from services.news_service import fetch_news, get_category, generate_remember,import_news_to_database
router = APIRouter()



@router.get("/latest-affairs")
def get_latest_affairs(
    day: str = Query(default="today", pattern="^(today|previous)$"),
    category: str | None = None,
    db: Session = Depends(get_db)
):
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    ist = ZoneInfo("Asia/Kolkata")
    today = datetime.now(ist).date()

    target_day = today if day == "today" else today - timedelta(days=1)

    def parse_and_filter(records, target_date):
        filtered = []
        for affair in records:
            published = affair.published_at

            try:
                # Support ISO timestamps with or without a timezone.
                published_dt = datetime.fromisoformat(
                    published.replace("Z", "+00:00")
                )

                if published_dt.tzinfo is None:
                    published_dt = published_dt.replace(tzinfo=ist)

                published_date = published_dt.astimezone(ist).date()

            except (ValueError, TypeError, AttributeError):
                # Support date-only values such as 2026-10-13.
                try:
                    published_date = datetime.strptime(
                        published, "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    continue

            if published_date != target_date:
                continue

            if category and category.strip().lower() != "all":
                if (affair.category or "").strip().lower() != category.strip().lower():
                    continue

            try:
                remember = json.loads(affair.remember)
            except (json.JSONDecodeError, TypeError):
                remember = []

            filtered.append({
                "id": affair.id,
                "category": affair.category,
                "title": affair.title,
                "summary": affair.summary,
                "remember": remember,
                "source": affair.source,
                "source_url": affair.source_url,
                "published_at": affair.published_at
            })
        return filtered

    affairs = (
        db.query(Affair)
        .filter(Affair.published_at.isnot(None))
        .order_by(Affair.published_at.desc(), Affair.id.desc())
        .all()
    )

    result = parse_and_filter(affairs, target_day)
    return result

@router.get("/search-affairs")
def search_affairs(
    q: str,
    db: Session = Depends(get_db)
):

    search_text = f"%{q}%"

    affairs = db.query(Affair).filter(
        (Affair.title.ilike(search_text)) |
        (Affair.summary.ilike(search_text)) |
        (Affair.category.ilike(search_text))
    ).order_by(
        Affair.id.desc()
    ).limit(20).all()

    result = []

    for affair in affairs:
        result.append({
            "id": affair.id,
            "category": affair.category,
            "title": affair.title,
            "summary": affair.summary,
            "remember": json.loads(affair.remember),
            "source": affair.source,
            "source_url": affair.source_url
        })

    return result
@router.get("/affairs/{affair_id}")
def get_affair(
    affair_id: int,
    db: Session = Depends(get_db)
):

    affair = db.query(Affair).filter(
        Affair.id == affair_id
    ).first()

    if not affair:
        raise HTTPException(
        status_code=404,
        detail="Article not found"
    )

    return {
        "id": affair.id,
        "category": affair.category,
        "title": affair.title,
        "summary": affair.summary,
        "remember": json.loads(affair.remember),
        "source": affair.source,
        "source_url": affair.source_url
    }
@router.get("/news-test")
def news_test():
    return fetch_news()


@router.post("/refresh-news")
@router.get("/refresh-news")
@router.get("/import-news")
def refresh_news_endpoint(db: Session = Depends(get_db)):
    return import_news_to_database(db)