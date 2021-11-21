# We translate boards into corner plays.  We'l consider a move a "corner play"
# when it's played in the corner 4x4 board.  Whenever one happens, we record a
# big surrounding portion, labeled by x's.
# xxxxxxxx.
# xxxxxxxx.
# xxxxxxxx.
# xxxxxxxx.
# xxxxxx...
# xxxxx....
# xxxx.....
# xxxx.....
# .........
#
# Expand this to an 11x11 before saving.  This is so that the CNN doesn't think
# the non-edges are edges.

import glob
from go_space.nn.data_manager import DataManager
import os
import pickle
from typing import Iterator, Tuple

import chardet

from go_space import board_lib, consts, exceptions
from go_space.go_types import *

from .datum_lib import Datum


Path = str

class SgfFormatError(exceptions.FormatError):
    pass


# TODO: Delete a bunch of unused to_dict/from_dict functions.


def read_game(fn):
    with open(fn, "rb") as f:
        bites = f.read()
    return bites.decode(encoding=chardet.detect(bites)["encoding"])


def _triggering_move(point: Point, player: Player) -> bool:
    if player == Player.White:
        return False
    r, c = point.mod_row_col()
    return r < 4 and c < 4


def _get_data_from_sgf(sgf: str) -> Iterator[Datum]:
    board = board_lib.Board()
    for pt, player in loop_game(sgf):
        if _triggering_move(pt):
            yield Datum(grid=board._grid.copy(), next_pt=pt)
        board.place(pt, player)


def point_player_from_sgf(move_str: str) -> Tuple[Point, Player]:
    """Expect sgf_string to be like 'B[aa]'."""
    move_str = move_str.strip()
    if len(move_str) != 5:
        raise SgfFormatError

    if move_str[0] == "B":
        # TODO: Consider moving some of these types.
        player = Player.Black
    elif move_str[0] == "W":
        player = Player.White
    else:
        raise SgfFormatError

    return Point.fromLabel(move_str[2:4]), player


def loop_game(sgf: str) -> Iterator[Tuple[Point, Player]]:
    for move_str in sgf.split(";"):
        try:
            pt, player = point_player_from_sgf(move_str[:5])
        except exceptions.FormatError:
            # Doesn't represent a move
            continue
        yield pt, player


NO_DATA_TO_SAVE = 1000

# TODO: Save test/train
def translate_files(src_dir: Path, tgt_dir: Path) -> None:
    dm = DataManager(tgt_dir)
    batch_num = 0

    # TODO: When a board breaks, save it to a file as a special case.
    for file in glob.glob(os.path.join(src_dir, "*.sgf")):
        for datum in _get_data_from_sgf(read_game(file)):
            if batch_num >= NO_DATA_TO_SAVE:
                break

            dm.save_datum()

            batch_num += 1
    
    dm.train_test_split(0.1)


translate_files(
    src_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_data"),
    tgt_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_processed_data"),
)
