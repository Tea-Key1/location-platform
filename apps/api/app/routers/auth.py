# app/routers/auth.py

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from jose import JWTError

from app.db.database import get_db

from app.schemas.auth import (
    AppleLoginRequest,
    AppleLoginResponse,
)

from app.models.user import User
from app.models.profile import Profile

from app.core.security import (
    create_access_token,
)

from app.core.errors import invalid_apple_token

from app.services.apple_auth import verify_apple_identity_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/apple",
    response_model=AppleLoginResponse,
)
async def apple_login(
    body: AppleLoginRequest,
    db: Session = Depends(get_db),
):
    try:
        apple_identity = await verify_apple_identity_token(
            body.identity_token
        )
    except JWTError:
        invalid_apple_token()

    user = (
        db.query(User)
        .filter(User.apple_sub == apple_identity.sub)
        .first()
    )

    if not user:

        user = User(
            apple_sub=apple_identity.sub,
            email=apple_identity.email,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
    elif apple_identity.email and user.email != apple_identity.email:
        user.email = apple_identity.email
        db.commit()
        db.refresh(user)

    token = create_access_token(
        {"sub": user.apple_sub}
    )

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user.id)
        .first()
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
