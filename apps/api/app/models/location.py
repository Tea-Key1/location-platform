from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Float,
    String,
    DateTime,
)

from app.core.security import utc_now
from app.db.database import Base


class Location(Base):

    __tablename__ = "locations"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
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

    timestamp = Column(
        DateTime,
        nullable=False,
        index=True,
    )

    s2_level12_id = Column(
        String,
        nullable=False,
        index=True,
    )

    prefecture = Column(
        String,
        nullable=True,
    )

    city = Column(
        String,
        nullable=True,
    )

    locality = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
    )
