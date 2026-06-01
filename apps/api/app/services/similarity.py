import numpy as np


def cosine_similarity(a, b):

    if a is None or b is None:

        return None

    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)

    if a_norm == 0 or b_norm == 0:

        return None

    similarity = float(
        np.dot(a, b)
        / (a_norm * b_norm)
    )

    return max(
        -1.0,
        min(1.0, similarity),
    )
