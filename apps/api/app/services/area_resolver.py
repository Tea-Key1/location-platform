from collections.abc import Callable

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import utc_now
from app.models.geocode_area_cache import GeocodeAreaCache
from app.models.location import Location
from app.models.similarity_check import SimilarityCheck
from app.services.geocoder import GeocoderRateLimited, GeocoderUnavailable
from app.services.s2cell import latlng_to_s2


EMPTY_AREA = {
    "prefecture": None,
    "city": None,
    "district": None,
}


def is_in_japan_bbox(lat: float, lng: float) -> bool:
    return 20.0 <= lat <= 46.5 and 122.0 <= lng <= 154.5


def cache_key_for_coordinate(lat: float, lng: float) -> str:
    return latlng_to_s2(lat, lng)


def public_area(area: dict | None) -> dict:
    if not area:
        return EMPTY_AREA.copy()

    return {
        "prefecture": area.get("prefecture"),
        "city": area.get("city"),
        "district": area.get("district"),
    }


def _area_has_value(area: dict | None) -> bool:
    return bool(area and any(public_area(area).values()))


def _area_from_cache(cache: GeocodeAreaCache | None) -> dict | None:
    if cache is None:
        return None

    return {
        "prefecture": cache.prefecture,
        "city": cache.city,
        "district": cache.district,
        "country_code": cache.country_code,
    }


def _cache_area(
    db: Session,
    *,
    key: str,
    lat: float,
    lng: float,
    area: dict,
) -> None:
    cache = (
        db.query(GeocodeAreaCache)
        .filter(GeocodeAreaCache.key == key)
        .one_or_none()
    )
    now = utc_now()

    if cache is None:
        cache = GeocodeAreaCache(
            key=key,
            s2_level12_id=key,
            created_at=now,
        )
        db.add(cache)

    cache.lat = lat
    cache.lng = lng
    cache.prefecture = area.get("prefecture")
    cache.city = area.get("city")
    cache.district = area.get("district")
    cache.country_code = area.get("country_code")
    cache.updated_at = now
    db.commit()


def _history_area_for_s2(
    db: Session,
    *,
    s2_id: str,
    lat: float,
    lng: float,
) -> dict | None:
    similarity_row = (
        db.query(SimilarityCheck)
        .filter(SimilarityCheck.current_s2_id == s2_id)
        .filter(
            (SimilarityCheck.current_prefecture.isnot(None))
            | (SimilarityCheck.current_city.isnot(None))
            | (SimilarityCheck.current_district.isnot(None))
        )
        .order_by(SimilarityCheck.checked_at.desc())
        .first()
    )

    if similarity_row is not None:
        return {
            "prefecture": similarity_row.current_prefecture,
            "city": similarity_row.current_city,
            "district": similarity_row.current_district,
        }

    location_row = (
        db.query(Location)
        .filter(Location.s2_level12_id == s2_id)
        .filter(
            (Location.prefecture.isnot(None))
            | (Location.city.isnot(None))
            | (Location.locality.isnot(None))
        )
        .order_by(Location.timestamp.desc())
        .first()
    )

    if location_row is not None:
        return {
            "prefecture": location_row.prefecture,
            "city": location_row.city,
            "district": location_row.locality,
        }

    distance = (
        func.abs(GeocodeAreaCache.lat - lat)
        + func.abs(GeocodeAreaCache.lng - lng)
    )
    nearby_cache = (
        db.query(GeocodeAreaCache)
        .filter(
            (GeocodeAreaCache.prefecture.isnot(None))
            | (GeocodeAreaCache.city.isnot(None))
            | (GeocodeAreaCache.district.isnot(None))
        )
        .filter(distance <= 0.05)
        .order_by(distance.asc())
        .first()
    )

    return _area_from_cache(nearby_cache)


def resolve_area(
    db: Session,
    *,
    lat: float,
    lng: float,
    reverse_geocode_func: Callable[[float, float], dict],
) -> dict:
    key = cache_key_for_coordinate(lat, lng)
    cache = (
        db.query(GeocodeAreaCache)
        .filter(GeocodeAreaCache.key == key)
        .one_or_none()
    )

    cached_area = _area_from_cache(cache)
    if cached_area is not None:
        return public_area(cached_area)

    try:
        geocoded_area = reverse_geocode_func(lat, lng)
    except (GeocoderRateLimited, GeocoderUnavailable):
        fallback_area = _history_area_for_s2(
            db,
            s2_id=key,
            lat=lat,
            lng=lng,
        )
        return public_area(fallback_area)

    if not _area_has_value(geocoded_area):
        return EMPTY_AREA.copy()

    country_code = geocoded_area.get("country_code")
    if country_code is not None:
        country_code = country_code.lower()
        geocoded_area["country_code"] = country_code

    if country_code in (None, "jp"):
        _cache_area(
            db,
            key=key,
            lat=lat,
            lng=lng,
            area=geocoded_area,
        )

    return public_area(geocoded_area)
