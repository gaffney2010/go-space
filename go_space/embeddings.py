"""This file contains the Embedding type and some sample embeddings."""

import os
from typing import Callable

from keras.models import load_model, Sequential
import numpy as np

from go_space import board_lib, consts
from go_space.go_types import stone_lib, player_lib, point_lib
from go_space.nn import datum_lib

# Must be a constant dimension
Embedding = Callable[[board_lib.Board], np.ndarray]


def make_random_embedding(dim: int) -> Embedding:
    PRECISION = 1000

    def infoless_embedding(brd: board_lib.Board) -> np.ndarray:
        """Just complete non-sense."""
        result = np.zeros(dim)  # Will fill in below

        scratch = hash(brd.ascii_board())
        for _ in range(dim):
            result[_] = (scratch % PRECISION) / PRECISION
            scratch = hash(str(scratch))

        return result

    return infoless_embedding


def dumb_embedding(brd: board_lib.Board) -> np.ndarray:
    """Simple encoding of boards, probably won't be good."""
    half_board = consts.SIZE // 2 + 1

    def _embed_ind(stone: stone_lib.Stone):
        player = stone.player
        row, col = stone.point.mod_row_col()

        # Only record up to symmetry
        ind = col * half_board + row
        if player == player_lib.Player.Black:
            ind += half_board ** 2

        return ind

    result = np.zeros(2 * (half_board ** 2))
    for stone in brd.stones():
        result[_embed_ind(stone)] += 1

    return result

def nn_embedding(brd: board_lib.Board) -> np.ndarray:
    # TODO: Don't reload with every call.
    full_model = load_model(os.path.join(consts.TOP_LEVEL_PATH, "saved_models", "v1"))
    layers = [full_model.get_layer(index=i) for i in range(8)]
    new_model = Sequential()
    for layer in layers:
        new_model.add(layer)
    
    # Pick a point in the corner, just so that it won't rotate
    pt = point_lib.Point(consts.SIZE-1, 0)
    datum = datum_lib.Datum(grid=brd._grid, next_pt=pt)
    x = np.stack([datum.np_feature()], axis=0)

    # print(x)
    y = new_model.predict(x)
    # print(y.shape)
    # print(y)
    # print(y[0])
    # assert(False)
    return y[0]
