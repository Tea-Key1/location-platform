# =========================================
# app/schemas/location.py
# =========================================

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =========================================
# CREATE
# =========================================

class LocationCreate(BaseModel):

    lat: float = Field(ge=-90.0, le=90.0)

    lng: float = Field(ge=-180.0, le=180.0)

    accuracy: float | None = None

    timestamp: datetime | None = None


# =========================================
# ITEM
# =========================================

class LocationItem(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int

    lat: float

    lng: float

    accuracy: float | None = None

    timestamp: datetime

    s2_level12_id: str

    prefecture: str | None = None

    city: str | None = None

    locality: str | None = None

    commercial_tracking_allowed_at_collection: bool

    tracking_consent_status_at_collection: str


# =========================================
# LIST RESPONSE
# =========================================

class LocationListResponse(
    BaseModel
):

    items: list[LocationItem]
