# app/routers/auth.py

from uuid import uuid4

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from jose import JWTError

from app.db.database import get_db

from app.schemas.auth import (
    AppleLoginRequest,
    AppleLoginResponse,
    LogoutAllResponse,
    LogoutResponse,
)

from app.dependencies.auth import (
    AuthContext,
    get_current_auth_context,
)

from app.models.auth_session import AuthSession
from app.models.user import User
from app.models.profile import Profile

from app.core.security import (
    create_access_token,
    get_access_token_expires_at,
    utc_now,
)

from app.core.errors import invalid_apple_token
from app.core.rate_limit import limiter

from app.services.apple_auth import verify_apple_identity_token
from app.services.apple_auth import AppleAuthUnavailable
from app.core.config import ENV

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def is_profile_completed(profile: Profile | None):
    return (
        profile is not None
        and profile.age_group is not None
        and profile.gender is not None
        and profile.calm is not None
        and profile.vivid is not None
        and profile.roamer is not None
        and profile.luxury is not None
        and profile.nature is not None
        and profile.nightlife is not None
        and profile.local is not None
        and profile.creative is not None
    )


@router.post(
    "/apple",
    response_model=AppleLoginResponse,
)
@limiter.limit("10/minute")
async def apple_login(
    request: Request,
    body: AppleLoginRequest,
    db: Session = Depends(get_db),
):
    try:
        apple_identity = await verify_apple_identity_token(
            body.identity_token
        )
    except AppleAuthUnavailable as exc:
        detail = (
            str(exc)
            if ENV != "production"
            else "Apple auth unavailable"
        )
        raise HTTPException(
            status_code=503,
            detail=detail,
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

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            user = (
                db.query(User)
                .filter(User.apple_sub == apple_identity.sub)
                .first()
            )

            if user is None:
                raise

    elif apple_identity.email and user.email != apple_identity.email:
        user.email = apple_identity.email
        db.commit()
        db.refresh(user)

    session_id = str(uuid4())
    jti = str(uuid4())
    expires_at = get_access_token_expires_at()

    auth_session = AuthSession(
        id=session_id,
        user_id=user.id,
        jti=jti,
        expires_at=expires_at,
    )

    db.add(auth_session)
    db.commit()

    token = create_access_token(
        {
            "sub": user.apple_sub,
            "sid": session_id,
            "jti": jti,
        },
        expires_at=expires_at,
    )

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user.id)
        .first()
    )

    profile_completed = is_profile_completed(profile)

    return AppleLoginResponse(
        access_token=token,
        token_type="bearer",
        profile_completed=profile_completed,
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
@limiter.limit("30/minute")
def logout(
    request: Request,
    context: AuthContext = Depends(get_current_auth_context),
    db: Session = Depends(get_db),
):

    if context.session.revoked_at is None:
        context.session.revoked_at = utc_now()
        db.commit()

    return LogoutResponse(
        logged_out=True,
    )


@router.post(
    "/logout-all",
    response_model=LogoutAllResponse,
)
@limiter.limit("30/minute")
def logout_all(
    request: Request,
    context: AuthContext = Depends(get_current_auth_context),
    db: Session = Depends(get_db),
):

    now = utc_now()

    sessions = (
        db.query(AuthSession)
        .filter(AuthSession.user_id == context.user.id)
        .filter(AuthSession.revoked_at.is_(None))
        .all()
    )

    revoked_sessions = 0

    for session in sessions:
        session.revoked_at = now
        revoked_sessions += 1

    db.commit()

    return LogoutAllResponse(
        logged_out=True,
        revoked_sessions=revoked_sessions,
    )
