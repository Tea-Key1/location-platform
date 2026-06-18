# =========================================
# app/schemas/similarity.py
# =========================================

from typing import Literal

from pydantic import BaseModel, Field


# =========================================
# AREA
# =========================================

class AreaResponse(BaseModel):

    prefecture: str | None = Field(examples=["Tokyo"])

    city: str | None = Field(examples=["Chiyoda"])

    district: str | None = Field(examples=["Marunouchi"])


# =========================================
# REQUEST
# =========================================

class SimilarityRequest(BaseModel):

    home_lat: float = Field(ge=-90.0, le=90.0, examples=[35.681236])
    home_lng: float = Field(ge=-180.0, le=180.0, examples=[139.767125])

    current_lat: float = Field(ge=-90.0, le=90.0, examples=[35.6895])
    current_lng: float = Field(ge=-180.0, le=180.0, examples=[139.6917])

    source: Literal["device", "manual"] | None = None


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

class SimilaritySearchRequest(BaseModel):

    lat: float = Field(ge=-90.0, le=90.0)

    lng: float = Field(ge=-180.0, le=180.0)

    top_k: int = Field(default=10, ge=1, le=50)


# =========================================
# SEARCH ITEM
# =========================================

class SimilarPlaceItem(BaseModel):

    id: str

    name: str

    lat: float

    lng: float

    similarity: float

    area: AreaResponse


# =========================================
# SEARCH RESPONSE
# =========================================

class SimilaritySearchResponse(BaseModel):

    items: list[SimilarPlaceItem]


# =========================================
# RANKINGS
# =========================================

RankingPeriod = Literal[
    "week",
    "month",
    "year",
]


class SimilarityRankingItem(BaseModel):

    rank: int = Field(ge=1)

    area: AreaResponse

    home_area: AreaResponse

    current_area: AreaResponse

    lat: float | None = Field(ge=-90.0, le=90.0)

    lng: float | None = Field(ge=-180.0, le=180.0)

    average_similarity: float = Field(ge=0.0, le=1.0)

    best_similarity: float | None = Field(ge=0.0, le=1.0)

    check_count: int = Field(ge=0)

    latest_checked_at: str | None


class SimilarityRankingsResponse(BaseModel):

    period: RankingPeriod

    items: list[SimilarityRankingItem]
