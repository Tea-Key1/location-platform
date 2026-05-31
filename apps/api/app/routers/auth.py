# app/routers/auth.py

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.schemas.auth import (
    AppleLoginRequest,
    AppleLoginResponse,
)

from app.models.user import User

from app.core.security import (
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/apple",
    response_model=AppleLoginResponse,
)
async def apple_login(
    body: AppleLoginRequest
):

    db: Session = SessionLocal()

    apple_sub = body.identity_token

    user = (
        db.query(User)
        .filter(User.apple_sub == apple_sub)
        .first()
    )

    if not user:

        user = User(
            apple_sub=apple_sub
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(
        {"sub": str(user.id)}
    )

    profile_completed = (
        profile is not None
        and profile.age_group is not None
        and profile.gender is not None
        and profile.home_lat is not None
        and profile.home_lng is not None
    )

    return AppleLoginResponse(
        access_token=token,
        token_type="bearer",
        profile_completed=profile_completed,
    )