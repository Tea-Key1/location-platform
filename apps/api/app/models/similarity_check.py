from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.security import utc_now
from app.db.database import Base


class SimilarityCheck(Base):

    __tablename__ = "similarity_checks"

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

    similarity = Column(
        Float,
        nullable=False,
    )

    home_prefecture = Column(
        String,
        nullable=True,
    )

    home_city = Column(
        String,
        nullable=True,
    )

    home_district = Column(
        String,
        nullable=True,
    )

    current_prefecture = Column(
        String,
        nullable=True,
        index=True,
    )

    current_city = Column(
        String,
        nullable=True,
        index=True,
    )

    current_district = Column(
        String,
        nullable=True,
        index=True,
    )

    current_lat = Column(
        Float,
        nullable=False,
    )

    current_lng = Column(
        Float,
        nullable=False,
    )

    current_s2_id = Column(
        String,
        nullable=False,
        index=True,
    )

    source = Column(
        String,
        nullable=True,
    )

    commercial_tracking_allowed_at_collection = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    tracking_consent_status_at_collection = Column(
        String,
        default="not_determined",
        nullable=False,
    )

    checked_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
        index=True,
    )
