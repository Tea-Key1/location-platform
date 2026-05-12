import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDINGS_PATH = (
    BASE_DIR / "data" / "embeddings.npy"
)

CELL_IDS_PATH = (
    BASE_DIR / "data" / "cell_ids.npy"
)


class EmbeddingStore:

    def __init__(self):

        self.embeddings = np.load(
            EMBEDDINGS_PATH
        )

        self.cell_ids = np.load(
            CELL_IDS_PATH
        )

        self.id_to_index = {
            int(cell_id): idx
            for idx, cell_id
            in enumerate(self.cell_ids)
        }

        print(
            f"Loaded {len(self.cell_ids)} embeddings"
        )

    def get_embedding(
        self,
        cell_id: int
    ):

        idx = self.id_to_index.get(cell_id)

        if idx is None:
            return None

        return self.embeddings[idx]


embedding_store = EmbeddingStore()