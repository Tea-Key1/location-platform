from sqlalchemy import (
    ForeignKey,
    Float,
    String,
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
    )

    # =====================================
    # demographics
    # =====================================

    age_group: Mapped[str | None]
    gender: Mapped[str | None]

    # =====================================
    # semantic personality
    # =====================================

    calm: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    vivid: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    roamer: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    luxury: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    nature: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    nightlife: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    local: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    creative: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )