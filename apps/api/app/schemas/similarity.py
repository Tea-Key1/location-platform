# =========================================
# app/schemas/similarity.py
# =========================================

from pydantic import BaseModel


# =========================================
# AREA
# =========================================

class AreaResponse(BaseModel):

    prefecture: str | None = None

    city: str | None = None

    district: str | None = None


# =========================================
# REQUEST
# =========================================

class SimilarityRequest(BaseModel):

    home_lat: float
    home_lng: float

    current_lat: float
    current_lng: float


# =========================================
# RESPONSE
# =========================================

class SimilarityResponse(BaseModel):

    similarity: float

    home_area: AreaResponse

    current_area: AreaResponse


# =========================================
# SEARCH REQUEST
# =========================================

class SimilaritySearchRequest(
    BaseModel
):

    lat: float

    lng: float

    top_k: int = 10


# =========================================
# SEARCH ITEM
# =========================================

class SimilarPlaceItem(
    BaseModel
):

    id: str

    name: str

    lat: float

    lng: float

    similarity: float

    area: AreaResponse


# =========================================
# SEARCH RESPONSE
# =========================================

class SimilaritySearchResponse(
    BaseModel
):

    items: list[SimilarPlaceItem]