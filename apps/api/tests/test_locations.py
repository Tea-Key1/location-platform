from uuid import uuid4

from app.core.security import create_access_token, get_access_token_expires_at
from app.db.database import SessionLocal
from app.models.auth_session import AuthSession
from app.models.user import User


def create_headers():
    db = SessionLocal()
    try:
        user = User(
            apple_sub=f"location-user-{uuid4()}",
            email="location@example.com",
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


def test_create_and_list_locations(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.location.reverse_geocode",
        lambda lat, lng: {
            "prefecture": "Tokyo",
            "city": "Shibuya",
            "district": "Ebisu",
        },
    )

    headers = create_headers()

    created = client.post(
        "/locations",
        headers=headers,
        json={
            "lat": 35.646,
            "lng": 139.710,
            "accuracy": 12.5,
            "timestamp": "2026-06-01T01:02:03Z",
        },
    )

    assert created.status_code == 200
    created_body = created.json()
    assert created_body["id"] > 0
    assert created_body["s2_level12_id"]
    assert created_body["prefecture"] == "Tokyo"
    assert created_body["city"] == "Shibuya"
    assert created_body["locality"] == "Ebisu"

    listed = client.get(
        "/locations",
        headers=headers,
    )

    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1


def test_location_lat_lng_validation(client):
    response = client.post(
        "/locations",
        headers=create_headers(),
        json={
            "lat": 120,
            "lng": 139.710,
        },
    )

    assert response.status_code == 422
