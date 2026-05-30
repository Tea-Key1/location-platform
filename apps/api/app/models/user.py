from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
)

from datetime import datetime, timezone

from app.db.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    apple_sub = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    email = Column(
        String,
        nullable=True,
    )

    # semantic home
    home_lat = Column(
        Float,
        nullable=True,
    )

    home_lng = Column(
        Float,
        nullable=True,
    )

    home_parent_s2_id = Column(
        String,
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=lambda:
            datetime.now(timezone.utc)
    )