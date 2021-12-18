"""This file contains the Embedding type and some sample embeddings."""

import os
from typing import Callable

from keras.models import load_model, Sequential
import numpy as np

from go_space import board, consts

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


def dumb_embedding(brd: board.Board) -> np.ndarray:
    """Simple encoding of boards, probably won't be good."""
    half_board = consts.SIZE // 2 + 1

    def _embed_ind(stone: board.Stone):
        player = stone.player
        row, col = stone.point.mod_row_col()

        # Only record up to symmetry
        ind = col * half_board + row
        if player == board.Player.Black:
            ind += half_board ** 2

        return ind

    result = np.zeros(2 * (half_board ** 2))
    for stone in brd.stones():
        result[_embed_ind(stone)] += 1

    return result

def nn_embedding(brd: board.Board) -> np.ndarray:
    # TODO: Don't reload with every call.
    full_model = load_model(os.path.join(consts.TOP_LEVEL_PATH, "saved_models", "v1"))
    layers = [full_model.get_layer(index=i) for i in range(3)]
    new_model = Sequential()
    for layer in layers:
        new_model.add(layer)
    
    y = new_model.predict(x)
    print(y)
    return y
