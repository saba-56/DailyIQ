
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session
from typing import Optional

from database.database import get_db
from models.opportunity import Opportunity
from models.student_profile import StudentProfile
from models.user import User, UserToken

router = APIRouter()


def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        return None

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token_record = (
        db.query(UserToken)
        .filter(UserToken.token == parts[1])
        .first()
    )

    if not token_record:
        return None

    return db.query(User).filter(
        User.id == token_record.user_id
    ).first()


def split_values(value):
    if not value:
        return set()

    return {
        part.strip().lower()
        for part in value.replace(";", ",").split(",")
        if part.strip()
    }


@router.get("/opportunities")
def get_opportunities(
    type: str | None = Query(default=None),
    personalized: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user)
):
    query = db.query(Opportunity)

    # Preserve the existing type filter.
    if type:
        query = query.filter(
            Opportunity.type.ilike(type.strip())
        )

    opportunities = query.order_by(
        Opportunity.id.desc()
    ).all()

    # Default behavior remains compatible with the old endpoint.
    if not personalized or not user:
        return [
            {
                "id": item.id,
                "type": item.type,
                "title": item.title,
                "organization": item.organization,
                "description": item.description,
                "eligibility": item.eligibility,
                "deadline": item.deadline,
                "link": item.link,
                "degree": item.degree,
                "branch": item.branch,
                "study_year": item.study_year,
                "required_skills": item.required_skills,
                "location": item.location,
                "source_url": item.source_url,
                "verified": item.verified,
                "match_score": None,
                "match_reasons": [],
            }
            for item in opportunities
        ]

    profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == user.id)
        .first()
    )

    # If this student has no profile, don't use another student's profile.
    if not profile:
        return [
            {
                "id": item.id,
                "type": item.type,
                "title": item.title,
                "organization": item.organization,
                "description": item.description,
                "eligibility": item.eligibility,
                "deadline": item.deadline,
                "link": item.link,
                "degree": item.degree,
                "branch": item.branch,
                "study_year": item.study_year,
                "required_skills": item.required_skills,
                "location": item.location,
                "source_url": item.source_url,
                "verified": item.verified,
                "match_score": None,
                "match_reasons": [],
            }
            for item in opportunities
        ]

    student_skills = split_values(profile.preferred_skills)
    preferred_location = (profile.preferred_location or "").strip().lower()

    ranked = []

    for item in opportunities:
        score = 0
        reasons = []

        # Award points only for fields explicitly provided by a listing.
        if item.degree and profile.degree:
            if item.degree.strip().lower() == profile.degree.strip().lower():
                score += 3
                reasons.append("Degree matches")

        if item.branch and profile.branch:
            if item.branch.strip().lower() == profile.branch.strip().lower():
                score += 3
                reasons.append("Branch matches")

        if item.study_year and profile.study_year:
            if item.study_year.strip().lower() == profile.study_year.strip().lower():
                score += 2
                reasons.append("Study year matches")

        required_skills = split_values(item.required_skills)
        matched_skills = student_skills.intersection(required_skills)

        if matched_skills:
            score += min(len(matched_skills) * 2, 6)
            reasons.append(
                "Matching skills: " + ", ".join(sorted(matched_skills))
            )

        if item.location and preferred_location:
            listing_location = item.location.strip().lower()

            if (
                listing_location in {"remote", "work from home", "anywhere"}
                or listing_location == preferred_location
                or preferred_location in listing_location
                or listing_location in preferred_location
            ):
                score += 2
                reasons.append("Location preference matches")

        ranked.append((item, score, reasons))

    # Highest match first; newest database ID breaks ties.
    ranked.sort(key=lambda entry: (entry[1], entry[0].id), reverse=True)

    return [
        {
            "id": item.id,
            "type": item.type,
            "title": item.title,
            "organization": item.organization,
            "description": item.description,
            "eligibility": item.eligibility,
            "deadline": item.deadline,
            "link": item.link,
            "degree": item.degree,
            "branch": item.branch,
            "study_year": item.study_year,
            "required_skills": item.required_skills,
            "location": item.location,
            "source_url": item.source_url,
            "verified": item.verified,
            "match_score": score,
            "match_reasons": reasons,
        }
        for item, score, reasons in ranked
    ]