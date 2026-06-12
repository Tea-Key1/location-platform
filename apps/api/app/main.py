# =========================================
# app/main.py
# =========================================

from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from slowapi.middleware import (
    SlowAPIMiddleware
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

from app.routers.privacy import (
    router as privacy_router
)

from app.routers.health import (
    router as health_router
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

from app.core.config import (
    CORS_ORIGINS,
    ENV,
)

# =========================================
# ENV
# =========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("===================================")
    print("Roamie API starting...")
    print(f"ENV: {ENV}")
    print("===================================")

    yield

    print("===================================")
    print("Roamie API shutting down...")
    print("===================================")


app = FastAPI(

    title="Roamie API",

    description=
    "GeoAI Personality Platform API",

    version="1.0.0",

    lifespan=lifespan,
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

    allow_origins=CORS_ORIGINS,

    allow_credentials="*" not in CORS_ORIGINS,

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
    privacy_router
)

app.include_router(
    health_router
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

