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
import os
from typing import Iterator, Tuple

import chardet

from go_space import board_lib, consts, exceptions, go_types
from go_space.nn import data_manager, datum_lib


Path = str


# TODO: Explore why 1486308520019999148.sgf is failing on parse.


class SgfFormatError(exceptions.FormatError):
    pass


def read_game(fn):
    with open(fn, "rb") as f:
        bites = f.read()
    return bites.decode(encoding=chardet.detect(bites)["encoding"])


def _triggering_move(datum: datum_lib.Datum, player: go_types.Player) -> bool:
    if player == go_types.Player.White:
        return False
    r, c = datum.next_pt.row, datum.next_pt.col
    # TODO: Magic numbers, bad
    return (r < 4 and c < 4) and datum.data_size() >= 8


def _get_data_from_sgf(sgf: str) -> Iterator[datum_lib.Datum]:
    """Loops through the moves played, yielding the "triggering moves"""
    board = board_lib.Board()
    for pt, player in loop_game(sgf):
        datum = datum_lib.Datum(grid=board._grid.copy(), next_pt=pt)
        if _triggering_move(datum, player):
            yield datum
        board.place(pt, player)


def point_player_from_sgf(move_str: str) -> Tuple[go_types.Point, go_types.Player]:
    """Expect sgf_string to be like 'B[aa]'."""
    move_str = move_str.strip()
    if len(move_str) != 5:
        raise SgfFormatError

    if move_str[0] == "B":
        # TODO: Consider moving some of these types.
        player = go_types.Player.Black
    elif move_str[0] == "W":
        player = go_types.Player.White
    else:
        raise SgfFormatError

    return go_types.Point.fromLabel(move_str[2:4]), player


def loop_game(sgf: str) -> Iterator[Tuple[go_types.Point, go_types.Player]]:
    for move_str in sgf.split(";"):
        try:
            pt, player = point_player_from_sgf(move_str[:5])
        except exceptions.FormatError:
            # Doesn't represent a move
            continue
        yield pt, player


NO_DATA_TO_SAVE = 40000


def translate_files(src_dir: Path, tgt_dir: Path) -> None:
    dm = data_manager.DataManager(tgt_dir)
    batch_num = 0

    for file in glob.glob(os.path.join(src_dir, "*.sgf")):
        try:
            # Queue because _get_data_from_sgf may fail part way
            data_queue = list()

            for datum in _get_data_from_sgf(read_game(file)):
                if batch_num >= NO_DATA_TO_SAVE:
                    return
                data_queue.append(datum)
                batch_num += 1
            
            for datum in data_queue:
                dm.save_datum(datum)
        except:
            print(f"Failed to parse file: {file}")


translate_files(
    src_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_data"),
    tgt_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_processed_data"),
)
