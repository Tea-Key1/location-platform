# =========================================
# app/main.py
# =========================================

import os

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from slowapi.middleware import (
    SlowAPIMiddleware
)

# =========================================
# DB
# =========================================

from app.db.database import (
    Base,
    engine,
)

# =========================================
# Routers
# =========================================

from app.routers.location import (
    router as location_router
)

from app.routers.auth import (
    router as auth_router
)

from app.routers.profile import (
    router as profile_router
)

from app.routers.similarity import (
    router as similarity_router
)

# =========================================
# Middleware
# =========================================

from app.core.logging import (
    LoggingMiddleware
)

from app.core.rate_limit import (
    limiter
)

# =========================================
# ENV
# =========================================

ENV = os.getenv(
    "ENV",
    "development"
)

# =========================================
# DB CREATE
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
# RATE LIMIT
# =========================================

app.state.limiter = limiter

app.add_middleware(
    SlowAPIMiddleware
)

# =========================================
# LOGGING
# =========================================

app.add_middleware(
    LoggingMiddleware
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

app.include_router(
    location_router
)

app.include_router(
    auth_router
)

app.include_router(
    profile_router
)

app.include_router(
    similarity_router
)

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
# STARTUP EVENT
# =========================================

@app.on_event("startup")
async def startup_event():

    print("===================================")
    print("🚀 Roamie API starting...")
    print(f"🌎 ENV: {ENV}")
    print("===================================")

# =========================================
# SHUTDOWN EVENT
# =========================================

@app.on_event("shutdown")
async def shutdown_event():

    print("===================================")
    print("🛑 Roamie API shutting down...")
    print("===================================")