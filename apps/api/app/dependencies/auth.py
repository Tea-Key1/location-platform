from dataclasses import dataclass

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from jose import jwt
from jose import JWTError

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.auth_session import AuthSession
from app.models.user import User

from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
    utc_now,
)

security = HTTPBearer()


@dataclass(frozen=True)
class AuthContext:
    user: User
    session: AuthSession


def unauthorized():

    raise HTTPException(
        status_code=401,
        detail="Unauthorized"
    )


def get_current_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        apple_sub = payload.get("sub")
        session_id = payload.get("sid")
        jti = payload.get("jti")

        if not apple_sub or not session_id or not jti:

            unauthorized()

        user = (
            db.query(User)
            .filter(User.apple_sub == apple_sub)
            .first()
        )

        if not user:

            unauthorized()

        session = (
            db.query(AuthSession)
            .filter(AuthSession.id == session_id)
            .filter(AuthSession.user_id == user.id)
            .filter(AuthSession.jti == jti)
            .first()
        )

        now = utc_now()

        if (
            not session
            or session.revoked_at is not None
            or session.expires_at <= now
        ):

            unauthorized()

        return AuthContext(
            user=user,
            session=session,
        )

    except JWTError:

        unauthorized()


def get_current_user(
    context: AuthContext = Depends(get_current_auth_context),
):

    return context.user
