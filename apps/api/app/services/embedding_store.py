import pandas as pd
import numpy as np

from pathlib import Path
from s2sphere import CellId


DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "patch_embeddings.parquet"
)

METADATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "patch_metadata.parquet"
)


def optional_value(value):
    if pd.isna(value):
        return None

    return value


def normalize_s2_id(value):
    return str(int(value))


class EmbeddingStore:

    def __init__(self):

        df = pd.read_parquet(DATA_PATH)
        metadata = pd.read_parquet(METADATA_PATH)
        metadata_map = {
            normalize_s2_id(row["parent_s2_id"]): row
            for _, row in metadata.iterrows()
        }

        embedding_columns = [
            column
            for column in df.columns
            if column.startswith("emb_")
        ]

        embedding_columns.sort(
            key=lambda column: int(column.removeprefix("emb_"))
        )

        self.embedding_map = {}
        self.items = []
        self.s2_level = None

        for _, row in df.iterrows():

            s2_id = normalize_s2_id(row["parent_s2_id"])
            s2_level = CellId(int(s2_id)).level()

            if self.s2_level is None:
                self.s2_level = s2_level

            vector = np.array(
                row[embedding_columns].to_numpy(),
                dtype=np.float32
            )

            self.embedding_map[s2_id] = vector
            metadata_row = metadata_map.get(s2_id)

            self.items.append({
                "s2_id": s2_id,
                "vector": vector,
                "lat": (
                    float(metadata_row["lat"])
                    if metadata_row is not None
                    else None
                ),
                "lng": (
                    float(metadata_row["lng"])
                    if metadata_row is not None
                    else None
                ),
                "prefecture": (
                    optional_value(metadata_row.get("prefecture"))
                    if metadata_row is not None
                    else None
                ),
                "city": (
                    optional_value(metadata_row.get("city_name"))
                    if metadata_row is not None
                    else None
                ),
            })

    def get(self, s2_id):

        return self.embedding_map.get(s2_id)


embedding_store = EmbeddingStore()
