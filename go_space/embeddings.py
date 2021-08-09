"""This file contains the Embedding type and some sample embeddings."""

from typing import Callable

import numpy as np

from go_space import board

# Must be a constant dimension
Embedding = Callable[[board.Board], np.ndarray]


def make_random_embedding(dim: int) -> Embedding:
    PRECISION = 1000

    def infoless_embedding(brd: board.Board) -> np.ndarray:
        """Just complete non-sense."""
        result = np.zeros(dim)  # Will fill in below

        scratch = hash(brd.ascii_board())
        for _ in range(dim):
            result[_] = (scratch % PRECISION) / PRECISION
            scratch = hash(str(scratch))

        return result

    return infoless_embedding

