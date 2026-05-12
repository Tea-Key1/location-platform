from app.services.pooling import pooled_embedding
import numpy as np

from app.services.embedding_store import (
    embedding_store
)

from app.services.s2cell import (
    latlng_to_cell_id,
    cell_id_to_latlng
)

def search_similar_locations(
    home_lat: float,
    home_lng: float,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    top_k: int = 20,
):
    home_cell = latlng_to_cell_id(
        home_lat,
        home_lng,
    )

    home_emb = pooled_embedding(
        home_cell
    )

    if home_emb is None:
        return []

    home_emb = np.asarray(home_emb, dtype=np.float32)

    results = []

    for cell_id, emb in zip(
        embedding_store.cell_ids,
        embedding_store.embeddings,
    ):

        loc = cell_id_to_latlng(
            int(cell_id)
        )

        lat = loc["lat"]
        lng = loc["lng"]

        if not (
            min_lat <= lat <= max_lat
            and min_lng <= lng <= max_lng
        ):
            continue

        target_emb = pooled_embedding(
            int(cell_id)
        )

        if target_emb is None:
            continue

        score = cosine_similarity(
            home_emb,
            target_emb,
        ) * 100

        results.append({
            "cell_id": int(cell_id),
            "lat": lat,
            "lng": lng,
            "similarity": round(
                float(score),
                2
            ),
        })

    results.sort(
        key=lambda x: x["similarity"],
        reverse=True,
    )

    return results[:top_k]

def cosine_similarity(a, b):

    print("=== cosine_similarity ===")

    print("a type:")
    print(type(a))

    print("b type:")
    print(type(b))

    print("a shape:")
    print(np.shape(a))

    print("b shape:")
    print(np.shape(b))

    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    print("a converted:")
    print(a[:5])

    print("b converted:")
    print(b[:5])

    numerator = np.dot(a, b)

    print("dot:")
    print(numerator)

    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    print("denominator:")
    print(denominator)

    similarity = numerator / denominator

    print("similarity:")
    print(similarity)

    return similarity


def calculate_similarity(
    home_lat: float,
    home_lng: float,
    current_lat: float,
    current_lng: float,
):

    print("\n=== calculate_similarity ===")

    home_cell = latlng_to_cell_id(
        home_lat,
        home_lng
    )

    current_cell = latlng_to_cell_id(
        current_lat,
        current_lng
    )

    print("home_cell:")
    print(home_cell)

    print("current_cell:")
    print(current_cell)

    home_emb = pooled_embedding(
        home_cell
    )

    current_emb = pooled_embedding(
        current_cell
    )

    print("home_emb exists:")
    print(home_emb is not None)

    print("current_emb exists:")
    print(current_emb is not None)

    print("home_emb:")
    print(home_emb)

    print("current_emb:")
    print(current_emb)

    similarity = cosine_similarity(
        home_emb,
        current_emb
    )

    print("final similarity:")
    print(similarity)

    return round(
        float(similarity) * 100,
        2
    )