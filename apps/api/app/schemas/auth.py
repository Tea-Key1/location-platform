# app/schemas/auth.py

from pydantic import BaseModel


# =========================================
# Apple Login
# =========================================

class AppleLoginRequest(BaseModel):

    identity_token: str