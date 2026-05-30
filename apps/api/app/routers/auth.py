from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.security import create_access_token
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import AppleLoginRequest

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/apple")
async def apple_login(
    req: AppleLoginRequest,
    db: Session = Depends(get_db),
):
    """
    MVP:
    Apple identity_token を仮の apple_sub として利用。
    Productionでは Apple公開鍵で verify して sub を使う。
    """

    apple_sub = req.identity_token

    stmt = select(User).where(
        User.apple_sub == apple_sub
    )

    user = db.scalar(stmt)

    if not user:
        user = User(
            apple_sub=apple_sub,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
    }


@router.get("/me")
async def me(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(stmt)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "id": user.id,
        "email": user.email,
        "apple_sub": user.apple_sub,
        "created_at": user.created_at,
        "home_lat": user.home_lat,
        "home_lng": user.home_lng,
        "home_parent_s2_id": user.home_parent_s2_id,
    }


@router.post("/refresh")
async def refresh_token(
    user_id: int = Depends(get_current_user),
):
    new_token = create_access_token(
        user_id
    )

    return {
        "access_token": new_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout():
    """
    MVP:
    stateless JWT のため server 側では何もしない。
    client 側で SecureStore から token を削除する。
    """

    return {
        "message": "Logged out"
    }