from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import relationship

from app.core.security import utc_now
from app.db.database import Base


class AuthSession(Base):

    __tablename__ = "auth_sessions"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    jti = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
        index=True,
    )

    revoked_at = Column(
        DateTime,
        nullable=True,
        index=True,
    )

    user = relationship(
        "User",
        back_populates="auth_sessions",
    )
