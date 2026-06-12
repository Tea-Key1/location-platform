# app/routers/profile.py

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.db.database import (
    get_db
)

from app.dependencies.auth import (
    get_current_user
)

from app.models.user import User
from app.models.profile import Profile
from app.models.auth_session import AuthSession
from app.models.location import Location

from app.schemas.profile import (
    ProfileResponse,
    HomeLocationRequest,
    HomeLocationResponse,
    OnboardingRequest,
    OnboardingResponse,
    ProfileCompletionResponse,
)

from app.schemas.common import (
    DeleteResponse
)

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
)

# =========================================
# ONBOARDING
# =========================================

@router.post(
    "/onboarding",
    response_model=OnboardingResponse,
)
def onboarding(

    body: OnboardingRequest,

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    profile = (
        db.query(Profile)
        .filter(
            Profile.user_id == user.id
        )
        .first()
    )

    # =====================================
    # UPSERT
    # =====================================

    if not profile:

        profile = Profile(
            user_id=user.id
        )

        db.add(profile)

    # =====================================
    # BASIC
    # =====================================

    profile.age_group = body.age_group
    profile.gender = body.gender

    # =====================================
    # HOME
    # =====================================

    profile.home_lat = body.home_lat
    profile.home_lng = body.home_lng

    # =====================================
    # PERSONALITY
    # =====================================

    profile.calm = body.calm
    profile.vivid = body.vivid

    profile.roamer = body.roamer
    profile.luxury = body.luxury
    profile.nature = body.nature
    profile.nightlife = body.nightlife
    profile.local = body.local
    profile.creative = body.creative

    db.commit()
    db.refresh(profile)

    return {

        "profile_completed": True,

        "profile": profile,
    }

# =========================================
# GET ME
# =========================================

@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_me(

    user: User = Depends(
        get_current_user
    ),
):

    if not user.profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return user.profile

# =========================================
# COMPLETION
# =========================================

@router.get(
    "/completion",
    response_model=ProfileCompletionResponse,
)
def completion(

    user: User = Depends(
        get_current_user
    ),
):

    completed = (

        user.profile is not None

        and user.profile.age_group is not None

        and user.profile.gender is not None

        and user.profile.home_lat is not None

        and user.profile.home_lng is not None
    )

    return {

        "profile_completed": completed
    }

# =========================================
# UPDATE HOME
# =========================================

@router.post(
    "/home",
    response_model=HomeLocationResponse,
)
def update_home(

    body: HomeLocationRequest,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    profile = (
        db.query(Profile)
        .filter(Profile.user_id == current_user.id)
        .first()
    )

    if not profile:

        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    profile.home_lat = body.home_lat
    profile.home_lng = body.home_lng

    db.commit()
    db.refresh(profile)

    return {

        "profile_completed": True,

        "profile": profile,
    }

# =========================================
# DELETE PROFILE
# =========================================

@router.delete(
    "/me",
    response_model=DeleteResponse,
)
def delete_profile(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):
    user_id = current_user.id

    (
        db.query(AuthSession)
        .filter(AuthSession.user_id == user_id)
        .delete(synchronize_session=False)
    )

    (
        db.query(Location)
        .filter(Location.user_id == user_id)
        .delete(synchronize_session=False)
    )

    (
        db.query(Profile)
        .filter(Profile.user_id == user_id)
        .delete(synchronize_session=False)
    )

    db.delete(current_user)
    db.commit()

    return {

        "deleted": True
    }
