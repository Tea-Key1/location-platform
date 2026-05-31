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

from app.core.auth import (
    get_current_user,
)

from app.db.database import (
    get_db,
)

from app.models.profile import Profile
from app.models.user import User

from app.schemas.profile import (
    ProfileCreateRequest,
    UpdateHomeRequest,
)

S2_LEVEL = 12

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
)

# =========================================
# S2
# =========================================

def latlng_to_parent(

    lat: float,

    lng: float,

    level: int = S2_LEVEL,

) -> str:

    cell = CellId.from_lat_lng(
        LatLng.from_degrees(lat, lng)
    )

    return str(
        cell.parent(level).id()
    )

# =========================================
# Create onboarding profile
# =========================================

@router.post("/onboarding")
async def create_profile(

    req: ProfileCreateRequest,

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),

):

    # =====================================
    # existing profile
    # =====================================

    stmt = select(Profile).where(
        Profile.user_id == user_id
    )

    existing = db.scalar(stmt)

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Profile already exists",
        )

    # =====================================
    # user
    # =====================================

    user_stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(user_stmt)

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # =====================================
    # home s2
    # =====================================

    parent_s2_id = latlng_to_parent(
        req.home_lat,
        req.home_lng,
    )

    # =====================================
    # update user
    # =====================================

    user.home_lat = req.home_lat

    user.home_lng = req.home_lng

    user.home_parent_s2_id = (
        parent_s2_id
    )

    # onboarding complete
    user.profile_completed = True

    # =====================================
    # create profile
    # =====================================

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

        "profile_completed":
            user.profile_completed,

        "profile_id":
            profile.id,

        "home": {

            "lat":
                user.home_lat,

            "lng":
                user.home_lng,

            "parent_s2_id":
                user.home_parent_s2_id,
        },
    }

# =========================================
# Update home
# =========================================

@router.post("/home")
async def update_home_location(

    req: UpdateHomeRequest,

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),

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

    parent_s2_id = latlng_to_parent(
        req.home_lat,
        req.home_lng,
    )

    user.home_lat = req.home_lat

    user.home_lng = req.home_lng

    user.home_parent_s2_id = (
        parent_s2_id
    )

    db.commit()

    return {

        "status": "updated",

        "home": {

            "lat":
                user.home_lat,

            "lng":
                user.home_lng,

            "parent_s2_id":
                user.home_parent_s2_id,
        },
    }

# =========================================
# Me
# =========================================

@router.get("/me")
async def get_my_profile(

    user_id: int =
        Depends(get_current_user),

    db: Session =
        Depends(get_db),

):

    # =====================================
    # user
    # =====================================

    user_stmt = select(User).where(
        User.id == user_id
    )

    user = db.scalar(user_stmt)

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # =====================================
    # profile
    # =====================================

    profile_stmt = select(Profile).where(
        Profile.user_id == user_id
    )

    profile = db.scalar(profile_stmt)

    return {

        "user": {

            "id":
                user.id,

            "email":
                user.email,

            "profile_completed":
                user.profile_completed,

            "home_lat":
                user.home_lat,

            "home_lng":
                user.home_lng,

            "home_parent_s2_id":
                user.home_parent_s2_id,
        },

        "profile":

            None if not profile else {

                "age_group":
                    profile.age_group,

                "gender":
                    profile.gender,

                "calm":
                    profile.calm,

                "vivid":
                    profile.vivid,

                "roamer":
                    profile.roamer,

                "luxury":
                    profile.luxury,

                "nature":
                    profile.nature,

                "nightlife":
                    profile.nightlife,

                "local":
                    profile.local,

                "creative":
                    profile.creative,
            },
    }