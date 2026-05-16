from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    Float,
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

    # =====================================
    # auth
    # =====================================

    apple_sub: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )

    email: Mapped[str | None]

    # =====================================
    # semantic home
    # =====================================

    home_lat: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    home_lng: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    home_parent_s2_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # =====================================
    # timestamps
    # =====================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )