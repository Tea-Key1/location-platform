from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import (
    get_db
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
async def health(
    db: Session = Depends(get_db),
):

    try:

        db.execute(text("SELECT 1"))

        db_status = "ok"

    except Exception:

        db_status = "error"

    return {

        "status": "ok",

        "db": db_status,
    }
