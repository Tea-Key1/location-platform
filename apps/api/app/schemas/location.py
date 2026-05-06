from pydantic import BaseModel


class LocationRequest(BaseModel):
    lat: float
    lng: float
    accuracy: float | None = None