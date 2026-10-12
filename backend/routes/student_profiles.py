from typing import Optional
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.student_profile import StudentProfile
from models.user import User, UserToken

router = APIRouter(tags=["student_profiles"])


class StudentProfileUpdate(BaseModel):
    degree: str = "B.Tech"
    branch: str = "CSE"
    study_year: str = "4th year"
    preferred_skills: str = "Python, Java, SQL, Web Development"
    preferred_location: str = "India"


def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not authorization:
        return None
    try:
        parts = authorization.strip().split(" ")
        token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else authorization.strip()
        user_token = db.query(UserToken).filter(UserToken.token == token).first()
        if user_token:
            return db.query(User).filter(User.id == user_token.user_id).first()
    except Exception:
        pass
    return None


@router.get("/student-profile")
def get_student_profile(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    profile = None
    if user:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()

    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == None).first()

    if not profile:
        profile = StudentProfile(
            user_id=user.id if user else None,
            profile_name=user.name if user else "Default Student",
            degree="B.Tech",
            branch="CSE",
            study_year="4th year",
            preferred_skills="Python, Java, SQL, Web Development",
            preferred_location="India",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {
        "id": profile.id,
        "profile_name": profile.profile_name,
        "degree": profile.degree,
        "branch": profile.branch,
        "study_year": profile.study_year,
        "preferred_skills": profile.preferred_skills,
        "preferred_location": profile.preferred_location,
    }


@router.put("/student-profile")
def update_student_profile(
    data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    profile = None
    if user:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()

    if not profile:
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == None).first()

    if not profile:
        profile = StudentProfile(
            user_id=user.id if user else None,
            profile_name=user.name if user else "Default Student"
        )
        db.add(profile)

    profile.degree = data.degree.strip()
    profile.branch = data.branch.strip()
    profile.study_year = data.study_year.strip()
    profile.preferred_skills = data.preferred_skills.strip()
    profile.preferred_location = data.preferred_location.strip()
    if user:
        profile.user_id = user.id
        profile.profile_name = user.name

    db.commit()
    db.refresh(profile)

    return {
        "message": "Student profile saved successfully",
        "degree": profile.degree,
        "branch": profile.branch,
        "study_year": profile.study_year,
        "preferred_skills": profile.preferred_skills,
        "preferred_location": profile.preferred_location,
    }