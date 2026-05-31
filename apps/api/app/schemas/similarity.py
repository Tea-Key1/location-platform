# app/schemas/similarity.py

from pydantic import BaseModel


class AreaResponse(BaseModel):
    prefecture: str | None = None
    city: str | None = None
    district: str | None = None


class SimilarityResponse(BaseModel):
    similarity: float
    home_area: AreaResponse
    current_area: AreaResponse


class SimilarPlaceItem(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    similarity: float
    area: AreaResponse


class SimilaritySearchResponse(BaseModel):
    items: list[SimilarPlaceItem]