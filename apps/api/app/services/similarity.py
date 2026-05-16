# app/services/similarity.py

from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity

from s2sphere import CellId, LatLng


# =========================================================
# CONFIG
# =========================================================

PATCH_EMBEDDING_PATH = Path(
    "app/data/patch_embeddings.parquet"
)

PATCH_METADATA_PATH = Path(
    "app/data/patch_metadata.parquet"
)

S2_LEVEL = 12


# =========================================================
# LOAD DATA
# =========================================================

print("📦 loading patch embeddings...")

emb_df = pd.read_parquet(
    PATCH_EMBEDDING_PATH
)

print("✅ embeddings:", emb_df.shape)

print("📦 loading patch metadata...")

meta_df = pd.read_parquet(
    PATCH_METADATA_PATH
)

print("✅ metadata:", meta_df.shape)


# =========================================================
# MERGE
# =========================================================

PATCH_DF = emb_df.merge(
    meta_df[
        [
            "parent_s2_id",
            "prefecture",
            "city_name",
            "city_code",
            "lat",
            "lng",
        ]
    ],
    on="parent_s2_id",
    how="left",
)

print("✅ merged:", PATCH_DF.shape)


# =========================================================
# EMBEDDING MATRIX
# =========================================================

EMBEDDING_COLS = sorted([
    c
    for c in PATCH_DF.columns
    if c.startswith("emb_")
])

EMBEDDING_MATRIX = PATCH_DF[
    EMBEDDING_COLS
].values.astype(np.float32)

print("✅ embedding matrix:", EMBEDDING_MATRIX.shape)


# =========================================================
# S2
# =========================================================

def latlng_to_parent(
    lat: float,
    lng: float,
    level: int = S2_LEVEL,
):

    cell = CellId.from_lat_lng(
        LatLng.from_degrees(lat, lng)
    )

    return cell.parent(level).id()


# =========================================================
# FIND EMBEDDING
# =========================================================

def find_embedding(
    lat: float,
    lng: float,
):

    parent_id = latlng_to_parent(
        lat,
        lng,
    )

    row = PATCH_DF[
        PATCH_DF["parent_s2_id"] == parent_id
    ]

    # =====================================================
    # exact match
    # =====================================================

    if len(row) > 0:

        emb = row[
            EMBEDDING_COLS
        ].values[0]

        return (
            emb,
            row.iloc[0].to_dict(),
        )

    # =====================================================
    # fallback:
    # nearest lat/lng
    # =====================================================

    coords = PATCH_DF[
        ["lat", "lng"]
    ].values

    query = np.array([
        lat,
        lng,
    ])

    dist = np.linalg.norm(
        coords - query,
        axis=1,
    )

    idx = dist.argmin()

    emb = EMBEDDING_MATRIX[idx]

    return (
        emb,
        PATCH_DF.iloc[idx].to_dict(),
    )


# =========================================================
# CALCULATE SIMILARITY
# =========================================================

def calculate_similarity(
    home_lat: float,
    home_lng: float,
    current_lat: float,
    current_lng: float,
):

    try:

        home_emb, home_meta = find_embedding(
            home_lat,
            home_lng,
        )

        current_emb, current_meta = find_embedding(
            current_lat,
            current_lng,
        )

        sim = cosine_similarity(
            home_emb.reshape(1, -1),
            current_emb.reshape(1, -1),
        )[0][0]

        # =============================================
        # -1~1 → -100~100
        # =============================================

        score = float(sim * 100.0)

        # clamp
        score = max(
            -100.0,
            min(100.0, score)
        )

        return round(score, 2)

    except Exception as e:

        print("similarity error:")
        print(e)

        return None


# =========================================================
# SEARCH SIMILAR LOCATIONS
# =========================================================

def clean_nan(v):

    if pd.isna(v):
        return None

    return v

def search_similar_locations(
    home_lat: float,
    home_lng: float,
    min_lat: float,
    max_lat: float,
    min_lng: float,
    max_lng: float,
    top_k: int = 20,
):

    # =====================================================
    # home embedding
    # =====================================================

    home_emb, home_meta = find_embedding(
        home_lat,
        home_lng,
    )

    # =====================================================
    # bounding box filter
    # =====================================================

    target = PATCH_DF[
        (PATCH_DF["lat"] >= min_lat)
        & (PATCH_DF["lat"] <= max_lat)
        & (PATCH_DF["lng"] >= min_lng)
        & (PATCH_DF["lng"] <= max_lng)
    ].copy()

    if len(target) == 0:
        return []

    target_embs = target[
        EMBEDDING_COLS
    ].values.astype(np.float32)

    # =====================================================
    # cosine similarity
    # =====================================================

    sims = cosine_similarity(
        home_emb.reshape(1, -1),
        target_embs,
    )[0]

    target["similarity"] = sims * 100.0

    # =====================================================
    # sort
    # =====================================================

    target = target.sort_values(
        "similarity",
        ascending=False,
    )

    target = target.head(top_k)

    # =====================================================
    # output
    # =====================================================

    results = []

    for _, row in target.iterrows():

        results.append({

            "similarity": round(
                float(row["similarity"]),
                2,
            ),

            "lat": float(row["lat"]),
            "lng": float(row["lng"]),

            "prefecture": clean_nan(
                row.get("prefecture")
            ),

            "city_name": clean_nan(
                row.get("city_name")
            ),

            "city_code": clean_nan(
                row.get("city_code")
            ),

            "parent_s2_id": int(
                row["parent_s2_id"]
            ),
        })

    return results