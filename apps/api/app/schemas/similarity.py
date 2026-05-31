# app/schemas/similarity.py

from typing import List
from pydantic import BaseModel


class AreaInfo(BaseModel):
    prefecture: str | None = None
    city: str | None = None
    district: str | None = None


class SimilarityResponse(BaseModel):

    similarity: float

    home_area: AreaInfo

    current_area: AreaInfo


class SimilaritySearchItem(BaseModel):

    id: str
    name: str

    similarity: float

    lat: float
    lng: float


class SimilaritySearchResponse(BaseModel):

    items: List[SimilaritySearchItem]