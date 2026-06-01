from datetime import timedelta
from uuid import uuid4

from jose import jwt

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.security import (
    create_access_token,
    get_access_token_expires_at,
    utc_now,
)
from app.db.database import SessionLocal
from app.models.auth_session import AuthSession
from app.models.user import User
from app.services.apple_auth import AppleIdentity


def count_sessions():
    db = SessionLocal()
    try:
        return db.query(AuthSession).count()
    finally:
        db.close()


def create_user_with_session():
    db = SessionLocal()
    try:
        user = User(
            apple_sub=f"apple-{uuid4()}",
            email="test@example.com",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        session_id = str(uuid4())
        jti = str(uuid4())
        expires_at = get_access_token_expires_at()
        session = AuthSession(
            id=session_id,
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
        )
        db.add(session)
        db.commit()

        token = create_access_token(
            {
                "sub": user.apple_sub,
                "sid": session_id,
                "jti": jti,
            },
            expires_at=expires_at,
        )
        return user.apple_sub, token
    finally:
        db.close()


def test_first_login_creates_user_session_and_token(client, monkeypatch):
    async def fake_verify(identity_token):
        return AppleIdentity(
            sub="apple-first-login",
            email="first@example.com",
        )

    monkeypatch.setattr(
        "app.routers.auth.verify_apple_identity_token",
        fake_verify,
    )

    response = client.post(
        "/auth/apple",
        json={"identity_token": "valid-apple-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["profile_completed"] is False
    assert count_sessions() == 1


def test_existing_user_login_creates_new_session(client, monkeypatch):
    async def fake_verify(identity_token):
        return AppleIdentity(
            sub="apple-existing-login",
            email="existing@example.com",
        )

    monkeypatch.setattr(
        "app.routers.auth.verify_apple_identity_token",
        fake_verify,
    )

    first = client.post(
        "/auth/apple",
        json={"identity_token": "valid-apple-token"},
    )
    second = client.post(
        "/auth/apple",
        json={"identity_token": "valid-apple-token"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert count_sessions() == 2


def test_logout_revokes_current_token(client):
    _, token = create_user_with_session()
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get(
        "/profiles/completion",
        headers=headers,
    ).status_code == 200

    assert client.post(
        "/auth/logout",
        headers=headers,
    ).status_code == 200

    assert client.get(
        "/profiles/completion",
        headers=headers,
    ).status_code == 401


def test_logout_all_revokes_all_user_tokens(client):
    apple_sub, first_token = create_user_with_session()

    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(User.apple_sub == apple_sub)
            .first()
        )
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
        second_token = create_access_token(
            {
                "sub": apple_sub,
                "sid": session_id,
                "jti": jti,
            },
            expires_at=expires_at,
        )
    finally:
        db.close()

    first_headers = {"Authorization": f"Bearer {first_token}"}
    second_headers = {"Authorization": f"Bearer {second_token}"}

    assert client.get(
        "/profiles/completion",
        headers=first_headers,
    ).status_code == 200
    assert client.get(
        "/profiles/completion",
        headers=second_headers,
    ).status_code == 200

    assert client.post(
        "/auth/logout-all",
        headers=first_headers,
    ).status_code == 200

    assert client.get(
        "/profiles/completion",
        headers=first_headers,
    ).status_code == 401
    assert client.get(
        "/profiles/completion",
        headers=second_headers,
    ).status_code == 401


def test_old_token_without_session_claims_is_rejected(client):
    db = SessionLocal()
    try:
        user = User(apple_sub="old-token-user")
        db.add(user)
        db.commit()
    finally:
        db.close()

    token = create_access_token({"sub": "old-token-user"})

    response = client.get(
        "/profiles/completion",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_without_database_session_is_rejected(client):
    db = SessionLocal()
    try:
        user = User(apple_sub="missing-session-user")
        db.add(user)
        db.commit()
    finally:
        db.close()

    token = create_access_token({
        "sub": "missing-session-user",
        "sid": str(uuid4()),
        "jti": str(uuid4()),
    })

    response = client.get(
        "/profiles/completion",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_expired_token_is_rejected(client):
    token = jwt.encode(
        {
            "sub": "expired-user",
            "sid": str(uuid4()),
            "jti": str(uuid4()),
            "exp": utc_now() - timedelta(seconds=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/profiles/completion",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
