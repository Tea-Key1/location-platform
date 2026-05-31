# app/models/user.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
)

from datetime import datetime

from app.db.database import Base


class User(Base):

    __tablename__ = "users"

    # =========================================
    # Primary Key
    # =========================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================================
    # Apple Login
    # =========================================

    apple_sub = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String,
        nullable=True
    )

    # =========================================
    # Profile
    # =========================================

    gender = Column(
        String,
        nullable=True
    )

    age_range = Column(
        String,
        nullable=True
    )

    # =========================================
    # personality vector
    # =========================================

    calm = Column(
        Float,
        default=0.0
    )

    vivid = Column(
        Float,
        default=0.0
    )

    roamer = Column(
        Float,
        default=0.0
    )

    luxury = Column(
        Float,
        default=0.0
    )

    nature = Column(
        Float,
        default=0.0
    )

    nightlife = Column(
        Float,
        default=0.0
    )

    local = Column(
        Float,
        default=0.0
    )

    creative = Column(
        Float,
        default=0.0
    )

    # =========================================
    # Home Location
    # =========================================

    home_lat = Column(
        Float,
        nullable=True
    )

    home_lng = Column(
        Float,
        nullable=True
    )

    # =========================================
    # Onboarding
    # =========================================

    profile_completed = Column(
        Boolean,
        default=False
    )

    # =========================================
    # Created At
    # =========================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )