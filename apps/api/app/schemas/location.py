from pydantic import BaseModel


# =====================================================
# create location
# =====================================================

class LocationRequest(BaseModel):

    lat: float
    lng: float

    accuracy: float | None = None


# =====================================================
# similarity
# =====================================================

class SimilarityRequest(BaseModel):

    home_lat: float
    home_lng: float

    current_lat: float
    current_lng: float


class SimilarityResponse(BaseModel):

    similarity: float

    home_prefecture: str | None = None
    home_city: str | None = None

    current_prefecture: str | None = None
    current_city: str | None = None


# =====================================================
# similarity search
# =====================================================

class SimilaritySearchRequest(BaseModel):

    home_lat: float
    home_lng: float

    min_lat: float
    max_lat: float

    min_lng: float
    max_lng: float

    top_k: int = 20