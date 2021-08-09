"""Computes Buhlmann credibility on some informationless embeddings."""

import numpy as np

from go_space import board, embeddings
from go_space.validation import buhlmann


if __name__ == "__main__":
    # We found that random scores drop quickly until ~40, then level out.
    for d in range(10, 110, 10):
        print("=================")
        print(d)
        print(buhlmann.computeBuhlmannOnClasses(embeddings.make_random_embedding(d)))
        print()
