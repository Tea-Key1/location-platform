from pydantic import BaseModel


class LocationRequest(BaseModel):
    lat: float
    lng: float
    accuracy: float | None = None

class SimilarityRequest(BaseModel):

    home_lat: float
    home_lng: float

    current_lat: float
    current_lng: float

class SimilaritySearchRequest(BaseModel):
    home_lat: float
    home_lng: float

    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float

    top_k: int = 20