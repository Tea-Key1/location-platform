from datetime import timedelta
from uuid import uuid4

from app.core.security import (
    create_access_token,
    get_access_token_expires_at,
    utc_now,
)
from app.db.database import SessionLocal
from app.models.auth_session import AuthSession
from app.models.similarity_check import SimilarityCheck
from app.models.user import User


def create_user_headers(
    *,
    prefix="ranking-user",
    tracking_status="not_determined",
):
    db = SessionLocal()
    try:
        user = User(
            apple_sub=f"{prefix}-{uuid4()}",
            email="ranking@example.com",
            tracking_status=tracking_status,
            tracking_authorized=tracking_status == "authorized",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

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

        return user.id, {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


def add_similarity_check(
    user_id,
    *,
    similarity,
    prefecture="Tokyo",
    city="Chiyoda",
    district="Marunouchi",
    lat=35.0,
    lng=139.0,
    checked_at=None,
):
    db = SessionLocal()
    try:
        db.add(
            SimilarityCheck(
                user_id=user_id,
                similarity=similarity,
                home_prefecture="Tokyo",
                home_city="Chiyoda",
                home_district="Marunouchi",
                current_prefecture=prefecture,
                current_city=city,
                current_district=district,
                current_lat=lat,
                current_lng=lng,
                current_s2_id=f"s2-{uuid4()}",
                commercial_tracking_allowed_at_collection=False,
                tracking_consent_status_at_collection="denied",
                checked_at=checked_at or utc_now(),
            )
        )
        db.commit()
    finally:
        db.close()


def test_rankings_returns_empty_items_when_history_is_empty(client):
    _, headers = create_user_headers()

    response = client.get(
        "/similarity/rankings?period=week",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "period": "week",
        "items": [],
    }


def test_rankings_are_user_scoped_and_sorted_by_average_similarity(client):
    user_id, headers = create_user_headers(prefix="owner")
    other_user_id, _ = create_user_headers(prefix="other")

    add_similarity_check(user_id, similarity=0.6, city="Chiyoda")
    add_similarity_check(user_id, similarity=1.0, city="Chiyoda")
    add_similarity_check(user_id, similarity=0.9, city="Shinjuku")
    add_similarity_check(other_user_id, similarity=1.0, city="Other")

    response = client.get(
        "/similarity/rankings?period=month",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["period"] == "month"
    assert [item["rank"] for item in body["items"]] == [1, 2]
    assert [item["area"]["city"] for item in body["items"]] == [
        "Shinjuku",
        "Chiyoda",
    ]
    assert body["items"][0]["average_similarity"] == 0.9
    assert body["items"][0]["best_similarity"] == 0.9
    assert body["items"][0]["check_count"] == 1
    assert body["items"][0]["lat"] == 35.0
    assert body["items"][0]["lng"] == 139.0
    assert body["items"][0]["latest_checked_at"].endswith("Z")
    assert body["items"][1]["average_similarity"] == 0.8
    assert body["items"][1]["best_similarity"] == 1.0
    assert body["items"][1]["check_count"] == 2
    assert body["items"][1]["lat"] == 35.0
    assert body["items"][1]["lng"] == 139.0


def test_rankings_return_average_lat_lng(client):
    user_id, headers = create_user_headers()

    add_similarity_check(
        user_id,
        similarity=0.6,
        lat=35.0,
        lng=139.0,
    )
    add_similarity_check(
        user_id,
        similarity=0.8,
        lat=36.0,
        lng=140.0,
    )

    response = client.get(
        "/similarity/rankings?period=month",
        headers=headers,
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["lat"] == 35.5
    assert item["lng"] == 139.5


def test_rankings_filter_by_period(client):
    user_id, headers = create_user_headers()

    add_similarity_check(
        user_id,
        similarity=0.95,
        city="Recent",
        checked_at=utc_now() - timedelta(days=3),
    )
    add_similarity_check(
        user_id,
        similarity=1.0,
        city="Old",
        checked_at=utc_now() - timedelta(days=10),
    )

    response = client.get(
        "/similarity/rankings?period=week",
        headers=headers,
    )

    assert response.status_code == 200
    assert [item["area"]["city"] for item in response.json()["items"]] == [
        "Recent"
    ]


def test_rankings_reject_invalid_period(client):
    _, headers = create_user_headers()

    response = client.get(
        "/similarity/rankings?period=day",
        headers=headers,
    )

    assert response.status_code == 422


def test_rankings_are_available_when_att_denied(client):
    user_id, headers = create_user_headers(tracking_status="denied")
    add_similarity_check(user_id, similarity=0.7)

    response = client.get(
        "/similarity/rankings?period=year",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["check_count"] == 1
