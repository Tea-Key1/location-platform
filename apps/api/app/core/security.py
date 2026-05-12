# core/security.py

from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "CHANGE_THIS"
ALGORITHM = "HS256"


def create_access_token(
    user_id: int
):

    expire = datetime.utcnow() + timedelta(days=7)

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )