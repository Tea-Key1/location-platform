# app/schemas/auth.py

from pydantic import BaseModel


class AppleLoginRequest(BaseModel):
    identity_token: str


class AppleLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile_completed: bool


class LogoutResponse(BaseModel):
    logged_out: bool


class LogoutAllResponse(BaseModel):
    logged_out: bool
    revoked_sessions: int
