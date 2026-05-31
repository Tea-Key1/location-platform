# app/schemas/auth.py

from pydantic import BaseModel


class AppleLoginRequest(BaseModel):
    identity_token: str


class AppleLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile_completed: bool