# app/schemas/profile.py

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


AgeGroup = Literal[
    "10s",
    "20s",
    "30s",
    "40s",
    "50s",
    "60s",
    "70s+"
]

Gender = Literal[
    "male",
    "female",
    "other"
]


class OnboardingRequest(BaseModel):

    age_group: AgeGroup

    gender: Gender

    home_lat: float = Field(ge=-90.0, le=90.0)
    home_lng: float = Field(ge=-180.0, le=180.0)

    calm: float = Field(ge=0.0, le=1.0)
    vivid: float = Field(ge=0.0, le=1.0)

    roamer: float = Field(ge=0.0, le=1.0)
    luxury: float = Field(ge=0.0, le=1.0)
    nature: float = Field(ge=0.0, le=1.0)
    nightlife: float = Field(ge=0.0, le=1.0)
    local: float = Field(ge=0.0, le=1.0)
    creative: float = Field(ge=0.0, le=1.0)


class ProfileResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    age_group: str
    gender: str

    home_lat: float
    home_lng: float

    calm: float
    vivid: float

    roamer: float
    luxury: float
    nature: float
    nightlife: float
    local: float
    creative: float


class OnboardingResponse(BaseModel):

    profile_completed: bool

    profile: ProfileResponse


class ProfileCompletionResponse(BaseModel):
    profile_completed: bool

class HomeLocationRequest(BaseModel):
    home_lat: float = Field(ge=-90.0, le=90.0)
    home_lng: float = Field(ge=-180.0, le=180.0)

class HomeLocationResponse(BaseModel):
    profile_completed: bool
    profile: ProfileResponse
