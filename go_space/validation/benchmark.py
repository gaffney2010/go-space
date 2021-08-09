"""Computes Buhlmann credibility on some informationless embeddings."""

import numpy as np

from go_space import board
from go_space.validation import buhlmann


def make_embedding(dim: int) -> buhlmann.Embedding:
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


if __name__ == "__main__":
    # We found that random scores drop quickly until ~40, then level out.
    for d in range(10, 110, 10):
        print("=================")
        print(d)
        print(buhlmann.computeBuhlmannOnClasses(make_embedding(d)))
        print()
