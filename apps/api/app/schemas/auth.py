from pydantic import BaseModel


class AppleLoginRequest(BaseModel):
    identity_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int