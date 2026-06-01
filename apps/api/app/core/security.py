# app/core/security.py

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from jose import jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_DAYS,
    ALGORITHM,
    SECRET_KEY,
)


# =========================================
# create jwt
# =========================================

def create_access_token(
    data: dict,
    expires_at: datetime | None = None,
):

    to_encode = data.copy()

    expire = expires_at or get_access_token_expires_at()

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def utc_now():

    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_access_token_expires_at():

    return (
        utc_now()
        + timedelta(
            days=ACCESS_TOKEN_EXPIRE_DAYS
        )
    )
