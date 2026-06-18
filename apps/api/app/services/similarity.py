import numpy as np
from math import ceil
from datetime import timedelta
from datetime import timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import utc_now
from app.models.geocode_area_cache import GeocodeAreaCache
from app.models.similarity_check import SimilarityCheck
from app.services.s2cell import latlng_to_s2


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

SIMILARITY_CHECK_COOLDOWN_SECONDS = 3 * 60


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


def _ranking_area_from_cache(db: Session, lat, lng):
    if lat is None or lng is None:
        return None

    key = latlng_to_s2(float(lat), float(lng))
    cache = (
        db.query(GeocodeAreaCache)
        .filter(GeocodeAreaCache.key == key)
        .one_or_none()
    )

    if cache is None:
        return None

    return {
        "prefecture": cache.prefecture,
        "city": cache.city,
        "district": cache.district,
    }


def create_similarity_check(
    db: Session,
    *,
    user,
    similarity: float,
    home_area: dict,
    current_area: dict,
    home_lat: float,
    home_lng: float,
    current_lat: float,
    current_lng: float,
    current_s2_id: str,
    source: str | None = None,
):
    check = SimilarityCheck(
        user_id=user.id,
        similarity=similarity,
        home_prefecture=_area_value(home_area, "prefecture"),
        home_city=_area_value(home_area, "city"),
        home_district=_area_value(home_area, "district"),
        home_lat=home_lat,
        home_lng=home_lng,
        current_prefecture=_area_value(current_area, "prefecture"),
        current_city=_area_value(current_area, "city"),
        current_district=_area_value(current_area, "district"),
        current_lat=current_lat,
        current_lng=current_lng,
        current_s2_id=current_s2_id,
        source=source,
        commercial_tracking_allowed_at_collection=(
            user.tracking_authorized is True
        ),
        tracking_consent_status_at_collection=user.tracking_status,
    )

    db.add(check)
    db.commit()
    db.refresh(check)

    return check


def get_similarity_retry_after_seconds(
    db: Session,
    *,
    user_id: int,
) -> int:
    latest_checked_at = (
        db.query(func.max(SimilarityCheck.checked_at))
        .filter(SimilarityCheck.user_id == user_id)
        .scalar()
    )

    if latest_checked_at is None:
        return 0

    elapsed = (utc_now() - latest_checked_at).total_seconds()
    retry_after = SIMILARITY_CHECK_COOLDOWN_SECONDS - elapsed

    if retry_after <= 0:
        return 0

    return max(1, ceil(retry_after))


def list_similarity_rankings(
    db: Session,
    *,
    user_id: int,
    period: str,
):
    cutoff = utc_now() - timedelta(days=PERIOD_DAYS[period])

    rows = (
        db.query(
            SimilarityCheck.home_prefecture.label("home_prefecture"),
            SimilarityCheck.home_city.label("home_city"),
            SimilarityCheck.home_district.label("home_district"),
            SimilarityCheck.current_prefecture.label("current_prefecture"),
            SimilarityCheck.current_city.label("current_city"),
            SimilarityCheck.current_district.label("current_district"),
            func.avg(SimilarityCheck.home_lat).label("home_lat"),
            func.avg(SimilarityCheck.home_lng).label("home_lng"),
            func.avg(SimilarityCheck.current_lat).label("lat"),
            func.avg(SimilarityCheck.current_lng).label("lng"),
            func.avg(SimilarityCheck.similarity).label("average_similarity"),
            func.max(SimilarityCheck.similarity).label("best_similarity"),
            func.count(SimilarityCheck.id).label("check_count"),
            func.max(SimilarityCheck.checked_at).label("latest_checked_at"),
        )
        .filter(SimilarityCheck.user_id == user_id)
        .filter(SimilarityCheck.checked_at >= cutoff)
        .group_by(
            SimilarityCheck.home_prefecture,
            SimilarityCheck.home_city,
            SimilarityCheck.home_district,
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

        home_area = {
            "prefecture": row.home_prefecture,
            "city": row.home_city,
            "district": row.home_district,
        }
        current_area = {
            "prefecture": row.current_prefecture,
            "city": row.current_city,
            "district": row.current_district,
        }

        if not any(home_area.values()):
            home_area = (
                _ranking_area_from_cache(db, row.home_lat, row.home_lng)
                or home_area
            )

        if not any(current_area.values()):
            current_area = (
                _ranking_area_from_cache(db, row.lat, row.lng)
                or current_area
            )

        items.append(
            {
                "rank": index,
                "area": current_area,
                "home_area": home_area,
                "current_area": current_area,
                "lat": None if row.lat is None else float(row.lat),
                "lng": None if row.lng is None else float(row.lng),
                "average_similarity": average_similarity,
                "best_similarity": best_similarity,
                "check_count": row.check_count,
                "latest_checked_at": _iso_z(row.latest_checked_at),
            }
        )

    return items
