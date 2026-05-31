# app/routers/similarity.py

from fastapi import APIRouter

from app.schemas.similarity import (
    SimilarityResponse,
    SimilaritySearchResponse
)

router = APIRouter(
    prefix="/similarity",
    tags=["similarity"]
)


@router.post(
    "",
    response_model=SimilarityResponse
)
def calculate_similarity():

    return {
        "similarity": 0.82,

        "home_area": {
            "prefecture": "Tokyo",
            "city": "Shibuya",
            "district": "Ebisu",
        },

        "current_area": {
            "prefecture": "Tokyo",
            "city": "Meguro",
            "district": "Nakameguro",
        },
    }


@router.post(
    "/search",
    response_model=SimilaritySearchResponse
)
def search_similarity():

    return {
        "items": [
            {
                "id": "tokyo_1",
                "name": "Shimokitazawa",

                "lat": 35.661,
                "lng": 139.668,

                "similarity": 0.91,

                "area": {
                    "prefecture": "Tokyo",
                    "city": "Setagaya",
                    "district": "Shimokitazawa",
                },
            }
        ]
    }