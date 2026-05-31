from fastapi import APIRouter

from app.services.s2cell import (
    latlng_to_s2
)

from app.services.embedding_store import (
    embedding_store
)

from app.services.similarity import (
    cosine_similarity
)

from app.services.geocoder import (
    reverse_geocode
)

router = APIRouter()


@router.post("/similarity")
def similarity(req: dict):

    home_lat = req["home_lat"]
    home_lng = req["home_lng"]

    current_lat = req["current_lat"]
    current_lng = req["current_lng"]

    # -------------------------
    # S2
    # -------------------------

    home_s2 = latlng_to_s2(
        home_lat,
        home_lng
    )

    current_s2 = latlng_to_s2(
        current_lat,
        current_lng
    )

    # -------------------------
    # embedding
    # -------------------------

    home_vec = embedding_store.get(
        home_s2
    )

    current_vec = embedding_store.get(
        current_s2
    )

    # -------------------------
    # similarity
    # -------------------------

    sim = cosine_similarity(
        home_vec,
        current_vec
    )

    # -------------------------
    # reverse geocode
    # -------------------------

    home_geo = reverse_geocode(
        home_lat,
        home_lng
    )

    current_geo = reverse_geocode(
        current_lat,
        current_lng
    )

    return {

        "home": {
            "s2_id": home_s2,
            "geo": home_geo,
        },

        "current": {
            "s2_id": current_s2,
            "geo": current_geo,
        },

        "similarity": sim
    }