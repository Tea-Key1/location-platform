# app/db/database.py

import os

from sqlalchemy import create_engine

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
