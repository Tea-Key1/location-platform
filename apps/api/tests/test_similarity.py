from uuid import uuid4

from app.core.security import create_access_token, get_access_token_expires_at
from app.db.database import SessionLocal
from app.models.auth_session import AuthSession
from app.models.similarity_check import SimilarityCheck
from app.models.user import User
from app.services.embedding_store import embedding_store


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

    db = SessionLocal()
    try:
        check = db.query(SimilarityCheck).one()
        assert check.similarity == 1.0
        assert check.current_prefecture == "Okinawa"
        assert check.current_city == "Taketomi"
        assert check.current_lat == item["lat"]
        assert check.current_lng == item["lng"]
        assert check.source == "manual"
        assert check.tracking_consent_status_at_collection == "not_determined"
    finally:
        db.close()


def test_out_of_coverage_home_or_current_returns_zero_similarity(
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
            "current_lat": 40.7128,
            "current_lng": -74.0060,
        },
    )

    assert response.status_code == 200
    assert response.json()["similarity"] == 0.0
