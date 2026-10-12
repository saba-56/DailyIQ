import json

from fastapi import APIRouter, Depends,Query, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.affair import Affair
from services.news_service import fetch_news, get_category, generate_remember,import_news_to_database
router = APIRouter()


@router.get("/latest-affairs")
def get_latest_affairs(
    category: str = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(Affair)

    if category:
        query = query.filter(Affair.category == category)

    affairs = query.order_by(
        Affair.id.desc()
    ).limit(10).all()

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


@router.get("/import-news")
def import_news(db: Session = Depends(get_db)):

    return import_news_to_database(db)