import pandas as pd
import numpy as np


class EmbeddingStore:

    def __init__(self):

        df = pd.read_parquet(
            "app/data/patch_embeddings.parquet"
        )

        self.embedding_map = {}

        for _, row in df.iterrows():

            s2_id = str(row["s2_id"])

            vector = np.array(
                row["embedding"],
                dtype=np.float32
            )

            self.embedding_map[s2_id] = vector

    def get(self, s2_id):

        return self.embedding_map.get(s2_id)


embedding_store = EmbeddingStore()