from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from jose import jwt
from jose import JWTError

from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.models.user import User

from app.core.security import (
    SECRET_KEY,
    ALGORITHM,
)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )

        db: Session = SessionLocal()

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if not user:

            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )

        return user

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )