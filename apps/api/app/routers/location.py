from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.location import Location
from app.schemas.location import (
    LocationRequest,
    SimilarityRequest,
    SimilaritySearchRequest
)
from app.services.similarity import (
    calculate_similarity,
    search_similar_locations
)

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

@router.post("/similarity")
async def similarity(
    req: SimilarityRequest
):

    score = calculate_similarity(
        req.home_lat,
        req.home_lng,
        req.current_lat,
        req.current_lng,
    )

    if score is None:
        return {
            "error": "embedding not found"
        }

    return {
        "similarity": score
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

@router.post("/similarity/search")
async def search_similarity(req: SimilaritySearchRequest):
    results = search_similar_locations(
        home_lat=req.home_lat,
        home_lng=req.home_lng,
        min_lat=req.min_lat,
        max_lat=req.max_lat,
        min_lng=req.min_lng,
        max_lng=req.max_lng,
        top_k=req.top_k,
    )

    return {
        "results": results
    }