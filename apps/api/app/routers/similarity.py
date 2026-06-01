# =========================================
# app/routers/similarity.py
# =========================================

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

from app.dependencies.auth import get_current_user

from app.models.user import User

from app.core.rate_limit import limiter

from app.schemas.similarity import (

    SimilarityRequest,

    SimilarityResponse,

    SimilaritySearchRequest,

    SimilaritySearchResponse,
)

from app.services.geocoder import (
    GeocoderRateLimited,
    GeocoderUnavailable,
    reverse_geocode
)

from app.services.s2cell import latlng_to_s2

from app.services.embedding_store import embedding_store

from app.services.similarity import cosine_similarity

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
):

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

    try:
        home_area = reverse_geocode(
            body.home_lat,
            body.home_lng
        )

        current_area = reverse_geocode(
            body.current_lat,
            body.current_lng
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

    return {

        "similarity": similarity,

        "home_area": home_area,

        "current_area": current_area,
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
