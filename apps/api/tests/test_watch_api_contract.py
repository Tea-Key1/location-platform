from uuid import uuid4

from app.core.security import create_access_token, get_access_token_expires_at
from app.db.database import SessionLocal
from app.models.auth_session import AuthSession
from app.models.profile import Profile
from app.models.user import User
from app.services.embedding_store import embedding_store


def create_user_headers(
    *,
    tracking_status="not_determined",
    profile=None,
):
    db = SessionLocal()
    try:
        user = User(
            apple_sub=f"watch-user-{uuid4()}",
            email="watch@example.com",
            tracking_status=tracking_status,
            tracking_authorized=tracking_status == "authorized",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        if profile is not None:
            db.add(
                Profile(
                    user_id=user.id,
                    **profile,
                )
            )

        session_id = str(uuid4())
        jti = str(uuid4())
        expires_at = get_access_token_expires_at()
        db.add(
            AuthSession(
                id=session_id,
                user_id=user.id,
                jti=jti,
                expires_at=expires_at,
            )
        )
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


def complete_profile(**overrides):
    data = {
        "age_group": "20s",
        "gender": "other",
        "home_lat": 35.681236,
        "home_lng": 139.767125,
        "calm": 0.1,
        "vivid": 0.2,
        "roamer": 0.3,
        "luxury": 0.4,
        "nature": 0.5,
        "nightlife": 0.6,
        "local": 0.7,
        "creative": 0.8,
    }
    data.update(overrides)
    return data


def test_watch_can_get_profile_home_with_bearer_token_when_att_denied(client):
    headers = create_user_headers(
        tracking_status="denied",
        profile=complete_profile(),
    )

    response = client.get(
        "/profiles/me",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["home_lat"] == 35.681236
    assert body["home_lng"] == 139.767125


def test_profile_me_rejects_profile_without_home_location(client):
    headers = create_user_headers(
        profile=complete_profile(
            home_lat=None,
            home_lng=None,
        ),
    )

    response = client.get(
        "/profiles/me",
        headers=headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Home location is not set"


def test_watch_similarity_response_shape_when_att_restricted(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routers.similarity.reverse_geocode",
        lambda lat, lng: {
            "prefecture": "東京都",
            "city": "千代田区" if lat == 35.681236 else "新宿区",
            "district": "丸の内" if lat == 35.681236 else "西新宿",
        },
    )

    item = next(
        item
        for item in embedding_store.items
        if item["lat"] is not None and item["lng"] is not None
    )

    response = client.post(
        "/similarity",
        headers=create_user_headers(tracking_status="restricted"),
        json={
            "home_lat": item["lat"],
            "home_lng": item["lng"],
            "current_lat": item["lat"],
            "current_lng": item["lng"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["similarity"] <= 1.0
    assert set(body) == {
        "similarity",
        "home_area",
        "current_area",
    }
    assert set(body["home_area"]) == {
        "prefecture",
        "city",
        "district",
    }
    assert set(body["current_area"]) == {
        "prefecture",
        "city",
        "district",
    }
