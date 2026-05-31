# app/routers/health.py

from sqlalchemy import text

from app.schemas.health import (
    HealthResponse
)

@app.get(
    "/health",
    response_model=HealthResponse
)
def health(db: Session = Depends(get_db)):

    try:

        db.execute(text("SELECT 1"))

        db_status = "ok"

    except Exception:

        db_status = "error"

    return {
        "status": "ok",
        "db": db_status
    }