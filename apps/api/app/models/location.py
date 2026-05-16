# app/models/location.py

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base


class Location(Base):

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # =====================================
    # raw gps
    # =====================================

    lat: Mapped[float] = mapped_column(
        Float
    )

    lng: Mapped[float] = mapped_column(
        Float
    )

    accuracy: Mapped[float | None]

    # =====================================
    # semantic
    # =====================================

    similarity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    parent_s2_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    prefecture: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    city_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # =====================================
    # timestamp
    # =====================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )