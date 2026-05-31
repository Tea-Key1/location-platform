# app/core/security.py

import os

from datetime import (
    datetime,
    timedelta,
)

from jose import jwt


# =========================================
# ENV
# =========================================

SECRET_KEY = os.getenv(
    "JWT_SECRET",
    "dev-secret"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_DAYS = 30


# =========================================
# create jwt
# =========================================

def create_access_token(
    data: dict
):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()
        + timedelta(
            days=ACCESS_TOKEN_EXPIRE_DAYS
        )
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt
