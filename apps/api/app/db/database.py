# app/db/database.py

import os

from sqlalchemy import create_engine
from sqlalchemy import text

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
)

# =========================================
# DATABASE URL
# =========================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app.db"
)

# =========================================
# engine
# =========================================

engine = create_engine(

    DATABASE_URL,

    connect_args={
        "check_same_thread": False
    }
    if DATABASE_URL.startswith("sqlite")
    else {},
)

# =========================================
# session
# =========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# =========================================
# base
# =========================================

Base = declarative_base()

# =========================================
# dependency
# =========================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


def ensure_sqlite_schema():
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as connection:
        profile_columns = {
            row[1]
            for row in connection.execute(
                text("PRAGMA table_info(profiles)")
            )
        }

        if not profile_columns:
            return

        if "home_lat" not in profile_columns:
            connection.execute(
                text("ALTER TABLE profiles ADD COLUMN home_lat FLOAT")
            )

        if "home_lng" not in profile_columns:
            connection.execute(
                text("ALTER TABLE profiles ADD COLUMN home_lng FLOAT")
            )
