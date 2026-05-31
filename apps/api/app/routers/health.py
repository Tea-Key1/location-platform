from fastapi import APIRouter

from sqlalchemy import text

from app.db.database import (
    SessionLocal
)

from app.schemas.health import (
    HealthResponse
)

router = APIRouter(
    tags=["health"]
)


@router.get(
    "/health",

    response_model=
    HealthResponse
)
async def health():

    db = SessionLocal()

    try:

        db.execute(text("SELECT 1"))

        db_status = "ok"

    except Exception:

        db_status = "error"

    return {

        "status": "ok",

        "db": db_status,
    }