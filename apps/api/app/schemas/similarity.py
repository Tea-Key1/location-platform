# =========================================
# app/schemas/similarity.py
# =========================================

from pydantic import BaseModel, Field


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

    home_lat: float = Field(ge=-90.0, le=90.0)
    home_lng: float = Field(ge=-180.0, le=180.0)

    current_lat: float = Field(ge=-90.0, le=90.0)
    current_lng: float = Field(ge=-180.0, le=180.0)


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

    lat: float = Field(ge=-90.0, le=90.0)

    lng: float = Field(ge=-180.0, le=180.0)

    top_k: int = Field(default=10, ge=1, le=50)


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
