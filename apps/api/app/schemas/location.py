# app/schemas/location.py

# =========================================
# app/schemas/location.py
# =========================================

from datetime import datetime

from pydantic import BaseModel

# =========================================
# CREATE
# =========================================

class LocationCreate(BaseModel):

    lat: float

    lng: float

    accuracy: float | None = None

# =========================================
# ITEM
# =========================================

class LocationItem(BaseModel):

    id: str

    lat: float

    lng: float

    accuracy: float | None = None

    created_at: datetime

# =========================================
# LIST RESPONSE
# =========================================

class LocationListResponse(
    BaseModel
):

    items: list[LocationItem]