from pydantic import BaseModel
from typing import Optional


class ProfileCreateRequest(BaseModel):

    # demographic
    age_group: Optional[str] = None
    gender: Optional[str] = None

    # semantic home
    home_lat: float
    home_lng: float

    # personality vector
    calm: float = 0.0
    vivid: float = 0.0
    roamer: float = 0.0

    luxury: float = 0.0
    nature: float = 0.0
    nightlife: float = 0.0

    local: float = 0.0
    creative: float = 0.0


class UpdateHomeRequest(BaseModel):
    home_lat: float
    home_lng: float