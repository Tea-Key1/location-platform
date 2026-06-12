from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.profile import Profile
from app.models.user import User


def query_partner_mobility_locations(db: Session):
    return (
        db.query(Location)
        .join(User, Location.user_id == User.id)
        .filter(User.tracking_authorized.is_(True))
        .filter(Location.commercial_tracking_allowed_at_collection.is_(True))
    )


def list_partner_mobility_locations(db: Session) -> list[Location]:
    return query_partner_mobility_locations(db).all()


def query_partner_mobility_profiles(db: Session):
    return (
        db.query(Profile)
        .join(User, Profile.user_id == User.id)
        .filter(User.tracking_authorized.is_(True))
    )
