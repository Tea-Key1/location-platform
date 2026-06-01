# =========================================
# app/routers/location.py
# =========================================

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from sqlalchemy.orm import Session

from app.db.database import (
    get_db
)

from app.dependencies.auth import (
    get_current_user
)

from app.models.user import User
from app.models.location import Location

from app.schemas.location import (
    LocationCreate,
    LocationItem,
    LocationListResponse,
)

from app.core.rate_limit import limiter

from app.services.geocoder import (
    GeocoderRateLimited,
    GeocoderUnavailable,
    reverse_geocode,
)

from app.services.s2cell import latlng_to_s2
from app.core.security import utc_now

# =========================================
# Router
# =========================================

router = APIRouter(

    prefix="/locations",

    tags=["locations"]
)

@router.get(
    "",
    response_model=LocationListResponse
)
@limiter.limit("60/minute")
async def get_locations(

    request: Request,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    locations = (
        db.query(Location)
        .filter(Location.user_id == current_user.id)
        .order_by(Location.timestamp.desc())
        .limit(100)
        .all()
    )

    return {

        "items": locations
    }

# =========================================
# CREATE LOCATION
# =========================================

@router.post(
    "",

    response_model=
    LocationItem
)
@limiter.limit("60/minute")
async def create_location(

    request: Request,

    payload: LocationCreate,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    timestamp = payload.timestamp or utc_now()

    if timestamp.tzinfo is not None:
        timestamp = (
            timestamp
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

    try:
        area = reverse_geocode(
            payload.lat,
            payload.lng
        )
    except GeocoderRateLimited as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        )
    except GeocoderUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    location = Location(
        user_id=current_user.id,
        lat=payload.lat,
        lng=payload.lng,
        accuracy=payload.accuracy,
        timestamp=timestamp,
        s2_level12_id=latlng_to_s2(
            payload.lat,
            payload.lng,
        ),
        prefecture=area.get("prefecture"),
        city=area.get("city"),
        locality=area.get("district"),
    )

    db.add(location)
    db.commit()
    db.refresh(location)

    return location
