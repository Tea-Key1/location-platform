# app/routers/auth.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.database import SessionLocal

from app.models.user import User

from app.schemas.auth import (
    AppleLoginRequest,
)

from app.core.security import (
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# =========================================
# DB
# =========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# =========================================
# Apple Login
# =========================================

@router.post("/apple")
def apple_login(
    body: AppleLoginRequest,
    db: Session = Depends(get_db)
):

    # =====================================
    # Apple token
    # MVP:
    # identity_tokenをsub代わりに使う
    # =====================================

    apple_sub = body.identity_token

    # =====================================
    # existing user
    # =====================================

    user = db.query(User).filter(
        User.apple_sub == apple_sub
    ).first()

    # =====================================
    # new user
    # =====================================

    if not user:

        user = User(
            apple_sub=apple_sub,
            profile_completed=False,
        )

        db.add(user)

        db.commit()

        db.refresh(user)

    # =====================================
    # JWT
    # =====================================

    access_token = create_access_token(
        {
            "user_id": user.id
        }
    )

    # =====================================
    # response
    # =====================================

    return {

        "access_token": access_token,

        "token_type": "bearer",

        "profile_completed":
            user.profile_completed,
    }