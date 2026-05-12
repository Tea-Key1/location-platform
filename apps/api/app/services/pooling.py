import numpy as np

from s2sphere import CellId

from app.services.embedding_store import (
    embedding_store
)


# =========================================
# neighbors
# =========================================
def get_neighbor_cells(
    cell_id: int
):

    cell = CellId(cell_id)

    neighbors = list(
        cell.get_all_neighbors(
            cell.level()
        )
    )

    return [
        n.id()
        for n in neighbors
    ]


# =========================================
# pooled embedding
# =========================================

def pooled_embedding(
    cell_id: int,
    center_weight: float = 2.0,
    neighbor_weight: float = 1.0,
):

    weighted_embeddings = []

    # =====================================
    # center
    # =====================================

    center_emb = embedding_store.get_embedding(
        cell_id
    )

    if center_emb is not None:

        weighted_embeddings.append(
            center_emb * center_weight
        )

    # =====================================
    # neighbors
    # =====================================

    neighbor_ids = get_neighbor_cells(
        cell_id
    )

    for nid in neighbor_ids:

        emb = embedding_store.get_embedding(
            nid
        )

        if emb is None:
            continue

        weighted_embeddings.append(
            emb * neighbor_weight
        )

    # =====================================
    # empty
    # =====================================

    if len(weighted_embeddings) == 0:
        return None

    # =====================================
    # mean pooling
    # =====================================

    pooled = np.mean(
        weighted_embeddings,
        axis=0
    )

    # =====================================
    # normalize
    # =====================================

    norm = np.linalg.norm(pooled)

    if norm > 0:

        pooled = pooled / norm

    return pooled