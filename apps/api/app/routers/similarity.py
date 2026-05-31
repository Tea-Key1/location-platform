# =========================================
# app/routers/similarity.py
# =========================================

from fastapi import APIRouter

from app.schemas.similarity import (

    SimilarityRequest,

    SimilarityResponse,

    SimilaritySearchRequest,

    SimilaritySearchResponse,
)

from app.services.geocoder import (
    reverse_geocode
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
async def calculate_similarity(

    body: SimilarityRequest
):

    home_area = reverse_geocode(
        body.home_lat,
        body.home_lng
    )

    current_area = reverse_geocode(
        body.current_lat,
        body.current_lng
    )

    return {

        "similarity": 0.82,

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
async def search_similarity(

    body: SimilaritySearchRequest
):

    return {

        "items": [

            {

                "id": "tokyo_1",

                "name":
                    "Shimokitazawa",

                "lat": 35.661,

                "lng": 139.668,

                "similarity": 0.91,

                "area": {

                    "prefecture":
                        "Tokyo",

                    "city":
                        "Setagaya",

                    "district":
                        "Shimokitazawa",
                },
            }
        ]
    }