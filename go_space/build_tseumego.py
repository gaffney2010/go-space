"""These are unclassified problems.  We embed these and pickle all of them.
"""

import json
import os
import pickle
from typing import Any, Dict

import attr
import numpy as np

from go_space import board_lib, consts, embeddings, exceptions
from go_space.go_types import chonk_lib, grid_lib, player_lib, point_lib


TseumegoString = Dict[str, Any]


@attr.s
class Tseumego(object):
    file_name: str = attr.ib()
    grid: grid_lib.Grid = attr.ib()
    embedding: np.ndarray = attr.ib()


nn_embed = embeddings.NNEmbed()
embedding_func = nn_embed.nn_embedding


def board_from_tseumego_string(tseumego: TseumegoString) -> board_lib.Board:
    translation_layer = {"black": "AB", "white": "AW"}
    return board_lib.boardFromBwBoardStr(tseumego, translation_layer)


def tseumego_from_file(fn: str) -> Tseumego:
    with open(fn, "r") as f:
        tseumego = json.loads(f.read())

    MUST_CONTAIN_FIELDS = ("AB", "AW", "SOL")
    for field in MUST_CONTAIN_FIELDS:
        if field not in tseumego:
            raise exceptions.TseumegoFormatError(
                f"Tseumego file {fn} missing required field {field}.  Actual content: {tseumego}."
            )

    # We require the next player to be black, and fix if it isn't.
    next_player = tseumego["SOL"][0][0]
    if next_player == "B":
        pass  # Okay
    elif next_player == "W":
        # Must switch players
        tseumego["AB"], tseumego["AW"] = tseumego["AW"], tseumego["AB"]
    else:
        sol = tseumego["SOL"]
        raise exceptions.TseumegoFormatError(
            f"Unexpected player found in solution field '{sol}' in tseumego file {fn}"
        )

    board = board_from_tseumego_string(tseumego)

    # Put a special character on the grid that only affects print to screen.
    next_pt = tseumego["SOL"][0][1]  # Only use the first move of solution for now.
    grid = board._grid
    grid[point_lib.Point.fromLabel(next_pt)] = chonk_lib.Chonk(
        player=player_lib.Player.Spec1, points=set(), liberties=set()
    )

    embedding = embedding_func(board)

    return Tseumego(file_name=fn, grid=grid, embedding=embedding)


print("Start")
all_files = list()
ct = 0
for root, dirs, files in os.walk(
    os.path.join(consts.TOP_LEVEL_PATH, "data", "_tseumego_problems")
):
    for file in files:
        if ct % 25 == 0:
            print(f"On file num {ct}")
        ct += 1
        all_files.append(tseumego_from_file(os.path.join(root, file)))

print("Pickle")
with open(
    os.path.join(consts.TOP_LEVEL_PATH, "data", "_pickled_tseumego", "basics.pickle"),
    "wb",
) as f:
    pickle.dump(all_files, f)

print("End")
