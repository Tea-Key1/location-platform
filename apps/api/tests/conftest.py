import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault(
    "JWT_SECRET",
    "test-secret-with-more-than-thirty-two-chars",
)
os.environ.setdefault("APPLE_CLIENT_ID", "com.taikiyanada.roamie")
os.environ.setdefault("DATABASE_URL", "sqlite:///C:/tmp/roamie-test.db")

from app.db.database import Base, engine
from app.main import app
from app.models.auth_session import AuthSession
from app.models.location import Location
from app.models.profile import Profile
from app.models.user import User


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)
