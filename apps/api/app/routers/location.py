# =========================================
# app/routers/location.py
# =========================================

from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.db.database import (
    SessionLocal
)

from app.dependencies.auth import (
    get_current_user
)

from app.models.user import User

from app.schemas.location import (
    LocationCreate,
    LocationItem,
    LocationListResponse,
)

# =========================================
# Router
# =========================================

router = APIRouter(

    prefix="/locations",

    tags=["locations"]
)

# =========================================
# DB Dependency
# =========================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()

# =========================================
# GET LOCATIONS
# =========================================

@router.get(
    "",
    response_model=LocationListResponse
)
async def get_locations(

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    return {

        "items": []
    }

# =========================================
# POST LOCATION
# =========================================

@router.post(
    ""
)
async def create_location(

    payload: LocationCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    return {

        "success": True,

        "lat": payload.lat,

        "lng": payload.lng,

        "accuracy": payload.accuracy,
    }