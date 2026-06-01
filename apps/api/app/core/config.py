import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("ENV", "development")
_jwt_secret = os.getenv("JWT_SECRET")
SECRET_KEY = _jwt_secret or "dev-secret"
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "30")
)
_apple_client_id = os.getenv("APPLE_CLIENT_ID")
APPLE_CLIENT_ID = _apple_client_id or "com.taikiyanada.roamie"
APPLE_ISSUER = "https://appleid.apple.com"

_database_url = os.getenv("DATABASE_URL")
DATABASE_URL = _database_url or "sqlite:///./app.db"

_cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
)

CORS_ORIGINS = [
    origin.strip()
    for origin in _cors_origins.split(",")
    if origin.strip()
]


def _validate_production_config():
    if ENV != "production":
        return

    missing = [
        name
        for name, value in (
            ("JWT_SECRET", _jwt_secret),
            ("DATABASE_URL", _database_url),
            ("APPLE_CLIENT_ID", _apple_client_id),
            ("CORS_ORIGINS", os.getenv("CORS_ORIGINS")),
        )
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing required production environment variables: "
            + ", ".join(missing)
        )

    if len(SECRET_KEY) < 32:
        raise RuntimeError(
            "JWT_SECRET must be at least 32 characters in production"
        )

    if "*" in CORS_ORIGINS:
        raise RuntimeError(
            "CORS_ORIGINS must not contain '*' in production"
        )


_validate_production_config()
