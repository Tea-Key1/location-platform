# app/routers/auth.py

from datetime import timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import HTTPBearer

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

# =========================================
# Router
# =========================================

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

security = HTTPBearer()

# =========================================
# Current User Dependency
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

    MVP:
    identity_token を仮subとして利用
    """

    apple_sub = req.identity_token

    db: Session = SessionLocal()

    stmt = select(User).where(
        User.apple_sub == apple_sub
    )

    user = db.scalar(stmt)

    # =====================================
    # Create User
    # =====================================

    if not user:

        user = User(
            apple_sub=apple_sub
        )

        db.add(user)

        db.commit()

        db.refresh(user)

    # =====================================
    # Create Access Token
    # =====================================

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "user_id": user.id,
    }

# =========================================
# Current User
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

# =========================================
# Refresh Token
# =========================================

@router.post("/refresh")
async def refresh_token(
    user_id=Depends(get_current_user)
):

    """
    MVP:
    access token 再発行
    """

    new_token = create_access_token(
        user_id
    )

    return {
        "access_token": new_token
    }

# =========================================
# Logout
# =========================================

@router.post("/logout")
async def logout():

    """
    MVP:
    stateless JWT のため
    client側で token delete
    """

    return {
        "message": "Logged out"
    }
