# app/models/profile.py

from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base


class Profile(Base):

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        index=True,
    )

    age_group: Mapped[str]

    gender: Mapped[str | None]

    lifestyle: Mapped[str | None]

    home_city: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )