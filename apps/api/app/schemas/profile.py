# app/schemas/profile.py

from pydantic import BaseModel


# =====================================================
# onboarding
# =====================================================

from pydantic import BaseModel


class ProfileCreateRequest(BaseModel):

    # =====================================
    # demographics
    # =====================================

    age_group: str | None = None
    gender: str | None = None

    # =====================================
    # semantic home
    # =====================================

    home_lat: float
    home_lng: float

    # =====================================
    # personality
    # =====================================

    calm: float | None = None
    vivid: float | None = None
    roamer: float | None = None
    luxury: float | None = None
    nature: float | None = None
    nightlife: float | None = None
    local: float | None = None
    creative: float | None = None


# =====================================================
# update semantic home
# =====================================================

class UpdateHomeRequest(BaseModel):

    home_lat: float
    home_lng: float