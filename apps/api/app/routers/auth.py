# app/routers/auth.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from jose import JWTError, jwt

from app.schemas.auth import (
    AppleLoginRequest
)

from app.models.user import User

from app.db.database import SessionLocal

from app.core.security import (
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)

from fastapi.security import HTTPBearer


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

security = HTTPBearer()


# =========================================
# current user dependency
# =========================================

def get_current_user(
    credentials=Depends(security)
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
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return int(user_id)

    except JWTError:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# =========================================
# Apple Sign In
# =========================================

@router.post("/apple")
async def apple_login(
    req: AppleLoginRequest
):

    """
    TODO:
    Apple identity token verify

    MVPでは仮subを使用
    """

    apple_sub = "temporary_sub"

    db: Session = SessionLocal()

    stmt = select(User).where(
        User.apple_sub == apple_sub
    )

    user = db.scalar(stmt)

    # =====================================
    # create user
    # =====================================

    if not user:

        user = User(
            apple_sub=apple_sub
        )

        db.add(user)

        db.commit()

        db.refresh(user)

    # =====================================
    # create jwt
    # =====================================

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "user_id": user.id,
    }


# =========================================
# current user
# =========================================

@router.get("/me")
async def me(
    user_id=Depends(get_current_user)
):

    db: Session = SessionLocal()

    stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(stmt)

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "email": user.email,
        "apple_sub": user.apple_sub,
        "created_at": user.created_at,
    }