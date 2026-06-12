from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from app.core.security import utc_now
from app.db.database import Base


class TrackingConsentAuditLog(Base):

    __tablename__ = "tracking_consent_audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    old_status = Column(
        String,
        nullable=True,
    )

    new_status = Column(
        String,
        nullable=False,
    )

    source = Column(
        String,
        nullable=False,
    )

    changed_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
        index=True,
    )
