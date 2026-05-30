from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    ForeignKey,
)

from app.db.database import Base


class Profile(Base):

    __tablename__ = "profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )

    # demographic
    age_group = Column(
        String,
        nullable=True,
    )

    gender = Column(
        String,
        nullable=True,
    )

    # personality vector
    calm = Column(
        Float,
        default=0.0,
    )

    vivid = Column(
        Float,
        default=0.0,
    )

    roamer = Column(
        Float,
        default=0.0,
    )

    luxury = Column(
        Float,
        default=0.0,
    )

    nature = Column(
        Float,
        default=0.0,
    )

    nightlife = Column(
        Float,
        default=0.0,
    )

    local = Column(
        Float,
        default=0.0,
    )

    creative = Column(
        Float,
        default=0.0,
    )