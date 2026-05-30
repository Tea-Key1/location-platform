from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
)

from datetime import datetime, timezone

from app.db.database import Base


class Location(Base):

    __tablename__ = "locations"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    lat = Column(
        Float,
        nullable=False,
    )

    lng = Column(
        Float,
        nullable=False,
    )

    accuracy = Column(
        Float,
        nullable=True,
    )

    similarity = Column(
        Float,
        nullable=True,
    )

    parent_s2_id = Column(
        String,
        nullable=True,
        index=True,
    )

    prefecture = Column(
        String,
        nullable=True,
    )

    city_name = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=lambda:
            datetime.now(timezone.utc)
    )