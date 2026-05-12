# schemas/auth.py

from pydantic import BaseModel


class AppleLoginRequest(BaseModel):

    identity_token: str