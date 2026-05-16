# app/routers/profile.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import select
from sqlalchemy.orm import Session

from s2sphere import (
    CellId,
    LatLng,
)

from app.db.database import SessionLocal

from app.models.profile import Profile
from app.models.user import User

from app.schemas.profile import (
    ProfileCreateRequest,
    UpdateHomeRequest,
)

from app.routers.auth import (
    get_current_user
)


# =====================================================
# CONFIG
# =====================================================

S2_LEVEL = 12


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"]
)


# =====================================================
# DB
# =====================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =====================================================
# S2
# =====================================================

def latlng_to_parent(
    lat: float,
    lng: float,
    level: int = S2_LEVEL,
):

    cell = CellId.from_lat_lng(
        LatLng.from_degrees(lat, lng)
    )

    return str(
        cell.parent(level).id()
    )


# =====================================================
# ONBOARDING
# =====================================================

@router.post("/onboarding")
async def create_profile(
    req: ProfileCreateRequest,
    user_id=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # =============================================
    # existing profile
    # =============================================

    stmt = select(Profile).where(
        Profile.user_id == user_id
    )

    existing = db.scalar(stmt)

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    # =============================================
    # user
    # =============================================

    user_stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(user_stmt)

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # =============================================
    # semantic home
    # =============================================

    parent_s2_id = latlng_to_parent(
        req.home_lat,
        req.home_lng,
    )

    user.home_lat = req.home_lat
    user.home_lng = req.home_lng
    user.home_parent_s2_id = parent_s2_id

    # =============================================
    # create profile
    # =============================================

    profile = Profile(

        user_id=user_id,

        age_group=req.age_group,
        gender=req.gender,

        calm=req.calm,
        vivid=req.vivid,
        roamer=req.roamer,
        luxury=req.luxury,
        nature=req.nature,
        nightlife=req.nightlife,
        local=req.local,
        creative=req.creative,
    )

    db.add(profile)

    db.commit()

    db.refresh(profile)

    return {

        "status": "created",

        "profile_id": profile.id,

        "home": {
            "lat": user.home_lat,
            "lng": user.home_lng,
            "parent_s2_id": user.home_parent_s2_id,
        }
    }


# =====================================================
# UPDATE HOME
# =====================================================

@router.post("/home")
async def update_home_location(
    req: UpdateHomeRequest,
    user_id=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # =============================================
    # user
    # =============================================

    stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(stmt)

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # =============================================
    # S2
    # =============================================

    parent_s2_id = latlng_to_parent(
        req.home_lat,
        req.home_lng,
    )

    # =============================================
    # update
    # =============================================

    user.home_lat = req.home_lat
    user.home_lng = req.home_lng
    user.home_parent_s2_id = parent_s2_id

    db.commit()

    return {

        "status": "updated",

        "home": {
            "lat": user.home_lat,
            "lng": user.home_lng,
            "parent_s2_id": user.home_parent_s2_id,
        }
    }


# =====================================================
# GET MY PROFILE
# =====================================================

@router.get("/me")
async def get_my_profile(
    user_id=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # =============================================
    # user
    # =============================================

    user_stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(user_stmt)

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # =============================================
    # profile
    # =============================================

    profile_stmt = select(Profile).where(
        Profile.user_id == user_id
    )

    profile = db.scalar(profile_stmt)

    return {

        "user": {

            "id": user.id,
            "email": user.email,

            "home_lat": user.home_lat,
            "home_lng": user.home_lng,
            "home_parent_s2_id": user.home_parent_s2_id,
        },

        "profile": None if not profile else {

            "age_group": profile.age_group,
            "gender": profile.gender,
            "lifestyle": profile.lifestyle,
            "home_city": profile.home_city,
        }
    }