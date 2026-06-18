# =========================================
# app/routers/similarity.py
# =========================================

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.database import get_db

from app.models.user import User

from app.core.rate_limit import limiter

from app.schemas.similarity import (

    SimilarityRequest,

    SimilarityResponse,

    RankingPeriod,

    SimilarityRankingsResponse,

    SimilaritySearchRequest,

    SimilaritySearchResponse,
)

from app.services.geocoder import reverse_geocode

from app.services.area_resolver import is_in_japan_bbox
from app.services.area_resolver import resolve_area
from app.services.s2cell import latlng_to_s2

from app.services.embedding_store import embedding_store

from app.services.similarity import (
    cosine_similarity,
    create_similarity_check,
    get_similarity_retry_after_seconds,
    list_similarity_rankings,
)

router = APIRouter(

    prefix="/similarity",

    tags=["similarity"]
)

# =========================================
# SIMILARITY
# =========================================

@router.post(
    "",
    response_model=SimilarityResponse
)
@limiter.limit("20/minute")
async def calculate_similarity(

    request: Request,

    body: SimilarityRequest,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db),
):
    if not is_in_japan_bbox(body.home_lat, body.home_lng):
        raise HTTPException(
            status_code=422,
            detail="home coordinate must be within Japan",
        )

    if not is_in_japan_bbox(body.current_lat, body.current_lng):
        raise HTTPException(
            status_code=422,
            detail="current coordinate must be within Japan",
        )

    retry_after_seconds = get_similarity_retry_after_seconds(
        db,
        user_id=current_user.id,
    )

    if retry_after_seconds > 0:
        raise HTTPException(
            status_code=429,
            detail={
                "message": (
                    "Similarity checks are limited to once every "
                    "3 minutes."
                ),
                "retry_after_seconds": retry_after_seconds,
                "retry_after": retry_after_seconds,
            },
            headers={"Retry-After": str(retry_after_seconds)},
        )

    home_s2 = latlng_to_s2(
        body.home_lat,
        body.home_lng,
        level=embedding_store.s2_level,
    )

    current_s2 = latlng_to_s2(
        body.current_lat,
        body.current_lng,
        level=embedding_store.s2_level,
    )

    similarity = cosine_similarity(
        embedding_store.get(home_s2),
        embedding_store.get(current_s2),
    )

    if similarity is None:
        similarity = 0.0
    else:
        similarity = max(0.0, min(1.0, similarity))

    home_area = resolve_area(
        db,
        lat=body.home_lat,
        lng=body.home_lng,
        reverse_geocode_func=reverse_geocode,
    )

    current_area = resolve_area(
        db,
        lat=body.current_lat,
        lng=body.current_lng,
        reverse_geocode_func=reverse_geocode,
    )

    create_similarity_check(
        db,
        user=current_user,
        similarity=similarity,
        home_area=home_area,
        current_area=current_area,
        home_lat=body.home_lat,
        home_lng=body.home_lng,
        current_lat=body.current_lat,
        current_lng=body.current_lng,
        current_s2_id=current_s2,
        source=body.source,
    )

    return {

        "similarity": similarity,

        "home_area": home_area,

        "current_area": current_area,
    }

# =========================================
# RANKINGS
# =========================================

@router.get(
    "/rankings",
    response_model=SimilarityRankingsResponse,
)
@limiter.limit("20/minute")
async def rankings(

    request: Request,

    period: RankingPeriod = Query(...),

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db),
):

    return {
        "period": period,
        "items": list_similarity_rankings(
            db,
            user_id=current_user.id,
            period=period,
        ),
    }

# =========================================
# SEARCH
# =========================================

@router.post(
    "/search",
    response_model=
    SimilaritySearchResponse
)
@limiter.limit("20/minute")
async def search_similarity(

    request: Request,

    body: SimilaritySearchRequest,

    current_user: User = Depends(get_current_user),
):

    source_s2 = latlng_to_s2(
        body.lat,
        body.lng,
        level=embedding_store.s2_level,
    )

    source_vector = embedding_store.get(source_s2)

    if source_vector is None:
        raise HTTPException(
            status_code=404,
            detail="Embedding not found",
        )

    scored_items = []

    for item in embedding_store.items:
        score = cosine_similarity(
            source_vector,
            item["vector"],
        )

        if score is None:
            continue

        scored_items.append(
            {
                "id": item["s2_id"],
                "name": item["city"] or item["s2_id"],
                "lat": item["lat"] or body.lat,
                "lng": item["lng"] or body.lng,
                "similarity": score,
                "area": {
                    "prefecture": item["prefecture"],
                    "city": item["city"],
                    "district": None,
                },
            }
        )

    scored_items.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return {

        "items": scored_items[:body.top_k]
    }
