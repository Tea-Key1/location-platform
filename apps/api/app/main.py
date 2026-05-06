from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.location import Location
from app.routers.location import router as location_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(location_router)


@app.get("/")
async def root():
    return {"message": "API running"}