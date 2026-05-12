# app/schemas/profile.py

from pydantic import BaseModel


class ProfileCreateRequest(BaseModel):

    age_group: str

    gender: str | None = None

    lifestyle: str | None = None

    home_city: str | None = None