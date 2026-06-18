from uuid import uuid4

from app.core.security import create_access_token, get_access_token_expires_at
from app.db.database import SessionLocal
from app.models.auth_session import AuthSession
from app.models.geocode_area_cache import GeocodeAreaCache
from app.models.similarity_check import SimilarityCheck
from app.models.user import User
from app.services.embedding_store import embedding_store
from app.services.geocoder import GeocoderRateLimited
from app.services.s2cell import latlng_to_s2


def create_headers():
    db = SessionLocal()
    try:
        user = User(
            apple_sub=f"similarity-user-{uuid4()}",
            email="similarity@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        session_id = str(uuid4())
        jti = str(uuid4())
        expires_at = get_access_token_expires_at()
        db.add(AuthSession(
            id=session_id,
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
        ))
        db.commit()

        token = create_access_token(
            {
                "sub": user.apple_sub,
                "sid": session_id,
                "jti": jti,
            },
            expires_at=expires_at,
        )

        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


def test_same_home_and_current_location_returns_full_similarity(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routers.similarity.reverse_geocode",
        lambda lat, lng: {
            "prefecture": "Okinawa",
            "city": "Taketomi",
            "district": None,
        },
    )

    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )

    response = client.post(
        "/similarity",
        headers=create_headers(),
        json={
            "home_lat": item["lat"],
            "home_lng": item["lng"],
            "current_lat": item["lat"],
            "current_lng": item["lng"],
            "source": "manual",
        },
    )

    assert response.status_code == 200
    assert response.json()["similarity"] == 1.0
    assert response.json()["home_area"] == {
        "prefecture": "Okinawa",
        "city": "Taketomi",
        "district": None,
    }
    assert response.json()["current_area"] == {
        "prefecture": "Okinawa",
        "city": "Taketomi",
        "district": None,
    }

    db = SessionLocal()
    try:
        check = db.query(SimilarityCheck).one()
        assert check.similarity == 1.0
        assert check.home_lat == item["lat"]
        assert check.home_lng == item["lng"]
        assert check.home_prefecture == "Okinawa"
        assert check.home_city == "Taketomi"
        assert check.current_prefecture == "Okinawa"
        assert check.current_city == "Taketomi"
        assert check.current_lat == item["lat"]
        assert check.current_lng == item["lng"]
        assert check.source == "manual"
        assert check.tracking_consent_status_at_collection == "not_determined"
    finally:
        db.close()


def test_japan_coordinate_without_embedding_returns_zero_similarity(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routers.similarity.reverse_geocode",
        lambda lat, lng: {
            "prefecture": None,
            "city": None,
            "district": None,
        },
    )

    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )

    response = client.post(
        "/similarity",
        headers=create_headers(),
        json={
            "home_lat": item["lat"],
            "home_lng": item["lng"],
            "current_lat": 45.0,
            "current_lng": 145.0,
        },
    )

    assert response.status_code == 200
    assert response.json()["similarity"] == 0.0


def test_similarity_rejects_coordinates_outside_japan(client):
    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )

    response = client.post(
        "/similarity",
        headers=create_headers(),
        json={
            "home_lat": item["lat"],
            "home_lng": item["lng"],
            "current_lat": 40.7128,
            "current_lng": -74.0060,
        },
    )

    assert response.status_code == 422


def test_geocoder_cache_hit_does_not_call_external_geocoder(
    client,
    monkeypatch,
):
    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )
    key = latlng_to_s2(item["lat"], item["lng"])

    db = SessionLocal()
    try:
        db.add(
            GeocodeAreaCache(
                key=key,
                s2_level12_id=key,
                lat=item["lat"],
                lng=item["lng"],
                prefecture="Tokyo",
                city="Chiyoda",
                district="Marunouchi",
                country_code="jp",
            )
        )
        db.commit()
    finally:
        db.close()

    def fail_geocoder(lat, lng):
        raise AssertionError("external geocoder should not be called")

    monkeypatch.setattr(
        "app.routers.similarity.reverse_geocode",
        fail_geocoder,
    )

    response = client.post(
        "/similarity",
        headers=create_headers(),
        json={
            "home_lat": item["lat"],
            "home_lng": item["lng"],
            "current_lat": item["lat"],
            "current_lng": item["lng"],
        },
    )

    assert response.status_code == 200
    assert response.json()["current_area"] == {
        "prefecture": "Tokyo",
        "city": "Chiyoda",
        "district": "Marunouchi",
    }


def test_geocoder_rate_limited_without_cache_returns_null_area_and_200(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routers.similarity.reverse_geocode",
        lambda lat, lng: (_ for _ in ()).throw(
            GeocoderRateLimited("rate limited")
        ),
    )

    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )

    response = client.post(
        "/similarity",
        headers=create_headers(),
        json={
            "home_lat": item["lat"],
            "home_lng": item["lng"],
            "current_lat": item["lat"],
            "current_lng": item["lng"],
        },
    )

    assert response.status_code == 200
    assert response.json()["home_area"] == {
        "prefecture": None,
        "city": None,
        "district": None,
    }
    assert response.json()["current_area"] == {
        "prefecture": None,
        "city": None,
        "district": None,
    }


def test_geocoder_rate_limited_with_cache_returns_area_and_200(
    client,
    monkeypatch,
):
    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )
    key = latlng_to_s2(item["lat"], item["lng"])

    db = SessionLocal()
    try:
        db.add(
            GeocodeAreaCache(
                key=key,
                s2_level12_id=key,
                lat=item["lat"],
                lng=item["lng"],
                prefecture="Tokyo",
                city="Setagaya",
                district="Shimokitazawa",
                country_code="jp",
            )
        )
        db.commit()
    finally:
        db.close()

    monkeypatch.setattr(
        "app.routers.similarity.reverse_geocode",
        lambda lat, lng: (_ for _ in ()).throw(
            GeocoderRateLimited("rate limited")
        ),
    )

    response = client.post(
        "/similarity",
        headers=create_headers(),
        json={
            "home_lat": item["lat"],
            "home_lng": item["lng"],
            "current_lat": item["lat"],
            "current_lng": item["lng"],
        },
    )

    assert response.status_code == 200
    assert response.json()["current_area"] == {
        "prefecture": "Tokyo",
        "city": "Setagaya",
        "district": "Shimokitazawa",
    }


def test_user_similarity_rate_limit_returns_429(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.similarity.reverse_geocode",
        lambda lat, lng: {
            "prefecture": "Tokyo",
            "city": "Chiyoda",
            "district": "Marunouchi",
        },
    )

    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )
    headers = create_headers()
    payload = {
        "home_lat": item["lat"],
        "home_lng": item["lng"],
        "current_lat": item["lat"],
        "current_lng": item["lng"],
    }

    first = client.post("/similarity", headers=headers, json=payload)
    second = client.post("/similarity", headers=headers, json=payload)

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["detail"]["retry_after_seconds"] > 0
