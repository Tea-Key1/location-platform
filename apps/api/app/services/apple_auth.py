from dataclasses import dataclass

import httpx
from jose import JWTError, jwt

from app.core.config import (
    APPLE_CLIENT_ID,
    APPLE_ISSUER,
)


APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"


@dataclass(frozen=True)
class AppleIdentity:
    sub: str
    email: str | None = None


async def verify_apple_identity_token(identity_token: str) -> AppleIdentity:
    try:
        header = jwt.get_unverified_header(identity_token)
        kid = header.get("kid")

        if not kid:
            raise JWTError("Missing key id")

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(APPLE_KEYS_URL)
            response.raise_for_status()

        keys = response.json().get("keys", [])
        key = next(
            (
                candidate
                for candidate in keys
                if candidate.get("kid") == kid
            ),
            None,
        )

        if key is None:
            raise JWTError("Apple signing key not found")

        payload = jwt.decode(
            identity_token,
            key,
            algorithms=["RS256"],
            audience=APPLE_CLIENT_ID,
            issuer=APPLE_ISSUER,
        )

        sub = payload.get("sub")

        if not sub:
            raise JWTError("Missing subject")

        return AppleIdentity(
            sub=sub,
            email=payload.get("email"),
        )

    except (httpx.HTTPError, JWTError, ValueError) as exc:
        raise JWTError("Invalid Apple identity token") from exc
