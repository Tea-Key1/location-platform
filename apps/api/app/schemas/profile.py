# app/schemas/profile.py

from pydantic import BaseModel


# =========================================
# onboarding profile
# =========================================

class ProfileCreateRequest(BaseModel):

    # basic
    age_group: str
    gender: str

    # home
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


# =========================================
# update home
# =========================================

class UpdateHomeRequest(BaseModel):

    home_lat: float
    home_lng: float

