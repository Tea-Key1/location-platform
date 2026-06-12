import numpy as np
from datetime import timedelta
from datetime import timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import utc_now
from app.models.similarity_check import SimilarityCheck


def cosine_similarity(a, b):

    if a is None or b is None:

        return None

    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)

    if a_norm == 0 or b_norm == 0:

        return None

    similarity = float(
        np.dot(a, b)
        / (a_norm * b_norm)
    )

    return max(
        -1.0,
        min(1.0, similarity),
    )


PERIOD_DAYS = {
    "week": 7,
    "month": 30,
    "year": 365,
}


def _area_value(area, key):
    if not area:
        return None

    return area.get(key)


def _iso_z(value):
    if value is None:
        return None

    return (
        value.replace(tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def create_similarity_check(
    db: Session,
    *,
    user,
    similarity: float,
    home_area: dict,
    current_area: dict,
    current_lat: float,
    current_lng: float,
    current_s2_id: str,
):
    check = SimilarityCheck(
        user_id=user.id,
        similarity=similarity,
        home_prefecture=_area_value(home_area, "prefecture"),
        home_city=_area_value(home_area, "city"),
        home_district=_area_value(home_area, "district"),
        current_prefecture=_area_value(current_area, "prefecture"),
        current_city=_area_value(current_area, "city"),
        current_district=_area_value(current_area, "district"),
        current_lat=current_lat,
        current_lng=current_lng,
        current_s2_id=current_s2_id,
        commercial_tracking_allowed_at_collection=(
            user.tracking_authorized is True
        ),
        tracking_consent_status_at_collection=user.tracking_status,
    )

    db.add(check)
    db.commit()
    db.refresh(check)

    return check


def list_similarity_rankings(
    db: Session,
    *,
    user_id: int,
    period: str,
):
    cutoff = utc_now() - timedelta(days=PERIOD_DAYS[period])

    rows = (
        db.query(
            SimilarityCheck.current_prefecture.label("prefecture"),
            SimilarityCheck.current_city.label("city"),
            SimilarityCheck.current_district.label("district"),
            func.avg(SimilarityCheck.similarity).label("average_similarity"),
            func.max(SimilarityCheck.similarity).label("best_similarity"),
            func.count(SimilarityCheck.id).label("check_count"),
            func.max(SimilarityCheck.checked_at).label("latest_checked_at"),
        )
        .filter(SimilarityCheck.user_id == user_id)
        .filter(SimilarityCheck.checked_at >= cutoff)
        .group_by(
            SimilarityCheck.current_prefecture,
            SimilarityCheck.current_city,
            SimilarityCheck.current_district,
        )
        .order_by(
            func.avg(SimilarityCheck.similarity).desc(),
            func.max(SimilarityCheck.checked_at).desc(),
        )
        .all()
    )

    items = []

    for index, row in enumerate(rows, start=1):
        average_similarity = max(
            0.0,
            min(1.0, float(row.average_similarity)),
        )
        best_similarity = (
            None
            if row.best_similarity is None
            else max(0.0, min(1.0, float(row.best_similarity)))
        )

        items.append(
            {
                "rank": index,
                "area": {
                    "prefecture": row.prefecture,
                    "city": row.city,
                    "district": row.district,
                },
                "average_similarity": average_similarity,
                "best_similarity": best_similarity,
                "check_count": row.check_count,
                "latest_checked_at": _iso_z(row.latest_checked_at),
            }
        )

    return items
