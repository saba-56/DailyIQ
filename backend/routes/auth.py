
import json
from typing import Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User, UserToken
from models.affair import Affair
from models.bookmark import Bookmark
from models.student_profile import StudentProfile

from services.auth_service import (
    hash_password,
    verify_password,
    create_token_for_user,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# -------------------- REQUEST MODELS --------------------

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    degree: Optional[str] = "Student"
    branch: Optional[str] = "General"
    study_year: Optional[str] = "Current"
    skills: Optional[str] = "General Knowledge"
    preferred_location: Optional[str] = "India"


class LoginRequest(BaseModel):
    email: str
    password: str


# -------------------- HELPER FUNCTION --------------------

def get_user_response(user: User, db: Session):
    """Return user details, bookmarks, and student profile."""

    bookmarks = (
        db.query(Bookmark.affair_id)
        .filter(Bookmark.user_id == user.id)
        .all()
    )
    bookmarked_ids = [item[0] for item in bookmarks]

    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == user.id)
        .first()
    )

    student_profile = None

    if profile:
        student_profile = {
            "degree": profile.degree,
            "branch": profile.branch,
            "study_year": profile.study_year,
            "preferred_skills": profile.preferred_skills,
            "preferred_location": profile.preferred_location,
        }

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "study_streak": user.study_streak,
        "articles_read": user.articles_read,
        "created_at": (
            user.created_at.isoformat()
            if user.created_at
            else None
        ),
        "bookmarked_ids": bookmarked_ids,
        "student_profile": student_profile,
    }


# -------------------- REGISTER --------------------

@router.post("/register")
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db),
):
    clean_name = req.name.strip()
    clean_email = req.email.strip().lower()

    # Validate name
    if not clean_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name cannot be empty.",
        )

    # Validate email
    if "@" not in clean_email or "." not in clean_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address.",
        )

    # Validate password
    if len(req.password.strip()) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long.",
        )

    degree = (req.degree or "Student").strip() or "Student"
    branch = (req.branch or "General").strip() or "General"
    study_year = (req.study_year or "Current").strip() or "Current"
    skills = (req.skills or "General Knowledge").strip() or "General Knowledge"
    preferred_location = (req.preferred_location or "India").strip() or "India"

    # Check for an existing account
    existing = (
        db.query(User)
        .filter(User.email == clean_email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    try:
        # Hash the password
        pwd_hash, salt = hash_password(req.password)

        # Create user
        new_user = User(
            name=clean_name,
            email=clean_email,
            password_hash=pwd_hash,
            salt=salt,
            study_streak=1,
            articles_read=0,
        )

        db.add(new_user)
        db.flush()

        # Save student profile
        student_profile = StudentProfile(
            user_id=new_user.id,
            profile_name=new_user.name,
            degree=degree,
            branch=branch,
            study_year=study_year,
            preferred_skills=skills,
            preferred_location=preferred_location,
        )

        db.add(student_profile)
        db.commit()
        db.refresh(new_user)
        db.refresh(student_profile)

        # Create login token
        token = create_token_for_user(db, new_user.id)

        return {
            "token": token,
            "user": get_user_response(new_user, db),
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again.",
        )


# -------------------- LOGIN --------------------

@router.post("/login")
def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
):
    clean_email = req.email.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == clean_email)
        .first()
    )

    if not user or not verify_password(
        req.password,
        user.salt,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_token_for_user(db, user.id)

    return {
        "token": token,
        "user": get_user_response(user, db),
    }


# -------------------- CURRENT USER --------------------

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_response(current_user, db)


# -------------------- LOGOUT --------------------

@router.post("/logout")
def logout(
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if authorization:
        parts = authorization.strip().split()

        token = (
            parts[1]
            if len(parts) == 2 and parts[0].lower() == "bearer"
            else authorization.strip()
        )

        db.query(UserToken).filter(
            UserToken.token == token
        ).delete()

        db.commit()

    return {"message": "Logged out successfully"}


# -------------------- TOGGLE BOOKMARK --------------------

@router.post("/bookmarks/{affair_id}")
def toggle_bookmark(
    affair_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    affair = (
        db.query(Affair)
        .filter(Affair.id == affair_id)
        .first()
    )

    if not affair:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found.",
        )

    existing = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == current_user.id,
            Bookmark.affair_id == affair_id,
        )
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()

        return {
            "bookmarked": False,
            "affair_id": affair_id,
            "message": "Bookmark removed",
        }

    new_bookmark = Bookmark(
        user_id=current_user.id,
        affair_id=affair_id,
    )

    db.add(new_bookmark)
    db.commit()

    return {
        "bookmarked": True,
        "affair_id": affair_id,
        "message": "Bookmark saved",
    }


# -------------------- GET SAVED BOOKMARKS --------------------

@router.get("/bookmarks")
def get_user_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmarks = (
        db.query(Bookmark)
        .filter(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.id.desc())
        .all()
    )

    affair_ids = [item.affair_id for item in bookmarks]

    if not affair_ids:
        return []

    affairs = (
        db.query(Affair)
        .filter(Affair.id.in_(affair_ids))
        .all()
    )

    affair_map = {affair.id: affair for affair in affairs}
    result = []

    # Preserve bookmark order
    for affair_id in affair_ids:
        affair = affair_map.get(affair_id)

        if affair is None:
            continue

        try:
            remember_data = (
                json.loads(affair.remember)
                if affair.remember
                else []
            )
        except (ValueError, TypeError):
            remember_data = []

        result.append({
            "id": affair.id,
            "category": affair.category,
            "title": affair.title,
            "summary": affair.summary,
            "remember": remember_data,
            "source": affair.source,
            "source_url": affair.source_url,
        })

    return result