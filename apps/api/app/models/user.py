# app/models/user.py

from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.database import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    apple_sub: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )

    email: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )