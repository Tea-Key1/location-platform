from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from app.core.security import utc_now
from app.db.database import Base


class GeocodeAreaCache(Base):

    __tablename__ = "geocode_area_cache"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    key = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    s2_level12_id = Column(
        String,
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

    prefecture = Column(
        String,
        nullable=True,
    )

    city = Column(
        String,
        nullable=True,
    )

    district = Column(
        String,
        nullable=True,
    )

    country_code = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
