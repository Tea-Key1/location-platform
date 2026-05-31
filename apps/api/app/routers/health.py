# app/routers/health.py

from fastapi import APIRouter
from sqlalchemy import text

from app.db.database import SessionLocal

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get("")
def health():

    db = SessionLocal()

    try:

        db.execute(text("SELECT 1"))

        db_status = "ok"

    except:

        db_status = "error"

    return {
        "status": "ok",
        "db": db_status,
    }