from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine

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
# DB
# =========================================

Base.metadata.create_all(bind=engine)

# =========================================
# APP
# =========================================

app = FastAPI()

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
        "message": "API running"
    }