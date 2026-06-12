from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import utc_now
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.tracking_consent_audit_log import TrackingConsentAuditLog
from app.models.user import User
from app.schemas.privacy import (
    TrackingConsentRequest,
    TrackingConsentResponse,
)


router = APIRouter(
    prefix="/privacy",
    tags=["privacy"],
)


@router.get(
    "/tracking-consent",
    response_model=TrackingConsentResponse,
)
def get_tracking_consent(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post(
    "/tracking-consent",
    response_model=TrackingConsentResponse,
)
def update_tracking_consent(
    body: TrackingConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = utc_now()
    old_status = current_user.tracking_status

    current_user.tracking_status = body.status
    current_user.tracking_authorized = body.status == "authorized"
    current_user.tracking_source = body.source
    current_user.tracking_updated_at = now

    db.add(TrackingConsentAuditLog(
        user_id=current_user.id,
        old_status=old_status,
        new_status=body.status,
        source=body.source,
        changed_at=now,
    ))

    db.commit()
    db.refresh(current_user)

    return current_user
