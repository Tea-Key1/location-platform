from uuid import uuid4

from app.core.security import create_access_token, get_access_token_expires_at
from app.db.database import SessionLocal
from app.models.auth_session import AuthSession
from app.models.location import Location
from app.models.profile import Profile
from app.models.similarity_check import SimilarityCheck
from app.models.tracking_consent_audit_log import TrackingConsentAuditLog
from app.models.user import User
from app.services.commercial_export import list_partner_mobility_locations


def create_user_headers(prefix="privacy-user"):
    db = SessionLocal()
    try:
        user = User(
            apple_sub=f"{prefix}-{uuid4()}",
            email="privacy@example.com",
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

        return user.id, {"Authorization": f"Bearer {token}"}
    finally:
        db.close()


def create_location(client, headers, lat):
    return client.post(
        "/locations",
        headers=headers,
        json={
            "lat": lat,
            "lng": 139.710,
            "accuracy": 12.5,
            "timestamp": "2026-06-01T01:02:03Z",
        },
    )


def test_tracking_consent_authorized_sets_tracking_authorized_true(client):
    _, headers = create_user_headers()

    response = client.post(
        "/privacy/tracking-consent",
        headers=headers,
        json={
            "status": "authorized",
            "source": "ios_att",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tracking_authorized"] is True
    assert body["tracking_status"] == "authorized"
    assert body["tracking_source"] == "ios_att"
    assert body["tracking_updated_at"] is not None


def test_tracking_consent_non_authorized_statuses_set_false(client):
    for status in [
        "denied",
        "restricted",
        "not_determined",
        "unavailable",
    ]:
        _, headers = create_user_headers(status)

        response = client.post(
            "/privacy/tracking-consent",
            headers=headers,
            json={
                "status": status,
                "source": "ios_att",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["tracking_authorized"] is False
        assert body["tracking_status"] == status


def test_tracking_consent_defaults_to_not_authorized(client):
    user_id, headers = create_user_headers()

    response = client.get(
        "/privacy/tracking-consent",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["tracking_authorized"] is False
    assert response.json()["tracking_status"] == "not_determined"

    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        assert user.tracking_authorized is False
    finally:
        db.close()


def test_tracking_consent_change_writes_audit_log(client):
    user_id, headers = create_user_headers()

    response = client.post(
        "/privacy/tracking-consent",
        headers=headers,
        json={
            "status": "denied",
            "source": "ios_att",
        },
    )

    assert response.status_code == 200

    db = SessionLocal()
    try:
        log = (
            db.query(TrackingConsentAuditLog)
            .filter(TrackingConsentAuditLog.user_id == user_id)
            .one()
        )
        assert log.old_status == "not_determined"
        assert log.new_status == "denied"
        assert log.source == "ios_att"
        assert log.changed_at is not None
    finally:
        db.close()


def test_commercial_export_only_includes_authorized_allowed_locations(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routers.location.reverse_geocode",
        lambda lat, lng: {
            "prefecture": "Tokyo",
            "city": "Shibuya",
            "district": "Ebisu",
        },
    )

    authorized_user_id, authorized_headers = create_user_headers("authorized")
    denied_user_id, denied_headers = create_user_headers("denied")

    before_authorize_location = create_location(
        client,
        authorized_headers,
        35.645,
    )
    assert before_authorize_location.status_code == 200

    allowed_update = client.post(
        "/privacy/tracking-consent",
        headers=authorized_headers,
        json={
            "status": "authorized",
            "source": "ios_att",
        },
    )
    assert allowed_update.status_code == 200

    allowed_location = create_location(client, authorized_headers, 35.646)
    denied_location = create_location(client, denied_headers, 35.647)
    assert allowed_location.status_code == 200
    assert denied_location.status_code == 200

    db = SessionLocal()
    try:
        exported = list_partner_mobility_locations(db)
        assert [location.user_id for location in exported] == [
            authorized_user_id
        ]
        assert exported[0].commercial_tracking_allowed_at_collection is True
        assert (
            exported[0].tracking_consent_status_at_collection
            == "authorized"
        )

        authorized_locations = (
            db.query(Location)
            .filter(Location.user_id == authorized_user_id)
            .order_by(Location.id.asc())
            .all()
        )
        assert [
            location.commercial_tracking_allowed_at_collection
            for location in authorized_locations
        ] == [False, True]

        denied_locations = (
            db.query(Location)
            .filter(Location.user_id == denied_user_id)
            .all()
        )
        assert denied_locations
        assert all(
            location.commercial_tracking_allowed_at_collection is False
            for location in denied_locations
        )
    finally:
        db.close()


def test_delete_profile_deletes_account_data_and_excludes_export(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.routers.location.reverse_geocode",
        lambda lat, lng: {
            "prefecture": "Tokyo",
            "city": "Shibuya",
            "district": "Ebisu",
        },
    )

    user_id, headers = create_user_headers("delete")

    consent = client.post(
        "/privacy/tracking-consent",
        headers=headers,
        json={
            "status": "authorized",
            "source": "ios_att",
        },
    )
    assert consent.status_code == 200

    profile = client.post(
        "/profiles/onboarding",
        headers=headers,
        json={
            "age_group": "20s",
            "gender": "other",
            "home_lat": 35.646,
            "home_lng": 139.710,
            "calm": 0.1,
            "vivid": 0.2,
            "roamer": 0.3,
            "luxury": 0.4,
            "nature": 0.5,
            "nightlife": 0.6,
            "local": 0.7,
            "creative": 0.8,
        },
    )
    assert profile.status_code == 200

    db = SessionLocal()
    try:
        db.add(
            SimilarityCheck(
                user_id=user_id,
                similarity=0.8,
                home_prefecture="Tokyo",
                home_city="Shibuya",
                home_district="Ebisu",
                current_prefecture="Tokyo",
                current_city="Shibuya",
                current_district="Ebisu",
                current_lat=35.646,
                current_lng=139.710,
                current_s2_id="test-s2",
                commercial_tracking_allowed_at_collection=True,
                tracking_consent_status_at_collection="authorized",
            )
        )
        db.commit()
    finally:
        db.close()

    location = create_location(client, headers, 35.646)
    assert location.status_code == 200

    deleted = client.delete(
        "/profiles/me",
        headers=headers,
    )
    assert deleted.status_code == 200
    assert deleted.json() == {"deleted": True}

    assert client.get(
        "/profiles/me",
        headers=headers,
    ).status_code == 401
    assert client.get(
        "/privacy/tracking-consent",
        headers=headers,
    ).status_code == 401

    db = SessionLocal()
    try:
        assert db.get(User, user_id) is None
        assert (
            db.query(Profile)
            .filter(Profile.user_id == user_id)
            .count()
            == 0
        )
        assert (
            db.query(Location)
            .filter(Location.user_id == user_id)
            .count()
            == 0
        )
        assert (
            db.query(SimilarityCheck)
            .filter(SimilarityCheck.user_id == user_id)
            .count()
            == 0
        )
        assert (
            db.query(AuthSession)
            .filter(AuthSession.user_id == user_id)
            .count()
            == 0
        )
        assert list_partner_mobility_locations(db) == []
    finally:
        db.close()
