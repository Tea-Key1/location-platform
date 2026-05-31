# app/routers/profile.py

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.dependencies.auth import (
    get_current_user
)

from app.models.user import User
from app.models.profile import Profile

from app.schemas.profile import (
    OnboardingRequest,
    OnboardingResponse,
    ProfileResponse,
    ProfileCompletionResponse,
)

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
)


@router.post(
    "/onboarding",
    response_model=OnboardingResponse,
)
def onboarding(
    body: OnboardingRequest,
    user: User = Depends(get_current_user),
):

    db: Session = SessionLocal()

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user.id)
        .first()
    )

    # upsert
    if not profile:

        profile = Profile(
            user_id=user.id
        )

        db.add(profile)

    profile.age_group = body.age_group
    profile.gender = body.gender

    profile.home_lat = body.home_lat
    profile.home_lng = body.home_lng

    profile.calm = body.calm
    profile.vivid = body.vivid

    profile.roamer = body.roamer
    profile.luxury = body.luxury
    profile.nature = body.nature
    profile.nightlife = body.nightlife
    profile.local = body.local
    profile.creative = body.creative

    db.commit()
    db.refresh(profile)

    return {
        "profile_completed": True,
        "profile": profile,
    }


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_me(
    user: User = Depends(get_current_user),
):

    if not user.profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return user.profile


@router.get(
    "/completion",
    response_model=ProfileCompletionResponse,
)
def completion(
    user: User = Depends(get_current_user),
):

    return {
        "profile_completed":
            user.profile is not None
    }


@router.delete("/me")
def reset_profile(
    user: User = Depends(get_current_user),
):

    db: Session = SessionLocal()

    profile = user.profile

    if profile:

        db.delete(profile)
        db.commit()

    return {
        "success": True
    }