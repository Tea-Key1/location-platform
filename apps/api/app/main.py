# app/main.py

import os

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.db.database import (
    Base,
    engine,
)

from app.routers.location import (
    router as location_router
)

from app.routers.auth import (
    router as auth_router
)

from app.routers.profile import (
    router as profile_router
)

# =========================================
# ENV
# =========================================

ENV = os.getenv(
    "ENV",
    "development"
)

# =========================================
# DB
# =========================================

Base.metadata.create_all(
    bind=engine
)

# =========================================
# APP
# =========================================

app = FastAPI(

    title="Roamie API",

    description=
    "GeoAI Personality Platform API",

    version="1.0.0",
)

# =========================================
# CORS
# =========================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# =========================================
# ROUTERS
# =========================================

app.include_router(location_router)

app.include_router(auth_router)

app.include_router(profile_router)

# =========================================
# ROOT
# =========================================

@app.get("/")
async def root():

    return {

        "message": "Roamie API running",

        "environment": ENV,
    }

# =========================================
# HEALTH CHECK
# =========================================

@app.get("/health")
async def health():

    return {

        "status": "ok"
    }

# =========================================
# STARTUP LOG
# =========================================

print("===================================")
print("🚀 Roamie API starting...")
print(f"🌎 ENV: {ENV}")
print("===================================")
