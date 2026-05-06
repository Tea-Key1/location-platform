from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.location import Location
from app.schemas.location import LocationRequest

router = APIRouter()


@router.post("/locations")
async def create_location(location: LocationRequest):
    db: Session = SessionLocal()

    db_location = Location(
        lat=location.lat,
        lng=location.lng,
        accuracy=location.accuracy,
    )

    db.add(db_location)
    db.commit()
    db.refresh(db_location)

    return {
        "status": "saved",
        "id": db_location.id,
    }


@router.get("/locations")
async def get_locations():
    db: Session = SessionLocal()

    stmt = select(Location).order_by(Location.created_at.desc())

    locations = db.scalars(stmt).all()

    return [
        {
            "id": loc.id,
            "lat": loc.lat,
            "lng": loc.lng,
            "accuracy": loc.accuracy,
            "created_at": loc.created_at,
        }
        for loc in locations
    ]