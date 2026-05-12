# app/routers/profile.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.models.profile import Profile

from app.schemas.profile import (
    ProfileCreateRequest
)

from app.routers.auth import (
    get_current_user
)

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"]
)


@router.post("/onboarding")
async def create_profile(
    req: ProfileCreateRequest,
    user_id=Depends(get_current_user)
):

    db: Session = SessionLocal()

    stmt = select(Profile).where(
        Profile.user_id == user_id
    )

    existing = db.scalar(stmt)

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    profile = Profile(
        user_id=user_id,
        age_group=req.age_group,
        gender=req.gender,
        lifestyle=req.lifestyle,
        home_city=req.home_city,
    )

    db.add(profile)

    db.commit()

    db.refresh(profile)

    return {
        "status": "created",
        "profile_id": profile.id,
    }