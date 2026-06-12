from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


TrackingStatus = Literal[
    "authorized",
    "denied",
    "restricted",
    "not_determined",
    "unavailable",
]


TrackingSource = Literal[
    "ios_att",
]


class TrackingConsentRequest(BaseModel):
    status: TrackingStatus
    source: TrackingSource


class TrackingConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tracking_authorized: bool
    tracking_status: TrackingStatus
    tracking_updated_at: datetime | None = None
    tracking_source: str | None = None
