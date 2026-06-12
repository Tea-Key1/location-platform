# =========================================
# app/schemas/similarity.py
# =========================================

from pydantic import BaseModel, Field


# =========================================
# AREA
# =========================================

class AreaResponse(BaseModel):

    prefecture: str | None = Field(default=None, examples=["東京都"])

    city: str | None = Field(default=None, examples=["千代田区"])

    district: str | None = Field(default=None, examples=["丸の内"])


# =========================================
# REQUEST
# =========================================

class SimilarityRequest(BaseModel):

    home_lat: float = Field(ge=-90.0, le=90.0, examples=[35.681236])
    home_lng: float = Field(ge=-180.0, le=180.0, examples=[139.767125])

    current_lat: float = Field(ge=-90.0, le=90.0, examples=[35.6895])
    current_lng: float = Field(ge=-180.0, le=180.0, examples=[139.6917])


# =========================================
# RESPONSE
# =========================================

class SimilarityResponse(BaseModel):

    similarity: float = Field(ge=0.0, le=1.0, examples=[0.82])

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
