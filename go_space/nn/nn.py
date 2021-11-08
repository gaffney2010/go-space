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

import glob
import os
import pickle
import time
from typing import Dict, Iterator, Tuple

import attr
import chardet

from go_space import board_lib, consts
from go_space.types import *

_SAMPLE_FILE = "1514127723010001630.sgf"


class SgfFormatError(FormatError):
    pass


def point_player_from_sgf(move_str: str) -> Tuple[Point, Player]:
    """Expect sgf_string to be like 'B[aa]'."""
    move_str = move_str.strip()
    if len(move_str) != 5:
        raise SgfFormatError
    
    if move_str[0] == 'B':
        # TODO: Consider moving some of these types.
        player = Player.Black
    elif move_str[0] == 'W':
        player = Player.White
    else:
        raise SgfFormatError

    return Point.fromLabel(move_str[2:4]), player


def loop_game(sgf: str) -> Iterator[Tuple[Point, Player]]:
    for move_str in sgf.split(";"):
        try:
            pt, player = point_player_from_sgf(move_str[:5])
        except FormatError:
            # Doesn't represent a move
            continue
        yield pt, player


@attr.s
class Datum(object):
    board: board_lib.Board = attr.ib()
    next_pt: Point = attr.ib()

    def to_dict(self) -> Dict:
        """Should contain all the info needed to reconstruct."""
        result = dict()
        result["board"] = self.board.to_dict()
        result["next_pt"] = self.next_pt.to_dict()
        return result

    @staticmethod
    def from_dict(data) -> "Datum":
        """Rebuild from one of the to_dict saved dicts."""
        return Datum(
            board=board_lib.Board.from_dict(data["board"]),
            next_pt=Point.from_dict(data["next_pt"]),
        )


def _triggering_move(point: Point) -> bool:
    r, c = point.mod_row_col()
    return r < 4 and c < 4


def _get_data_from_sgf(sgf: str) -> Iterator[Datum]:
    board = board_lib.Board()
    for pt, player in loop_game(sgf):        
        if _triggering_move(pt):
            yield Datum(board=board.copy(), next_pt=pt)
        board.place(pt, player)


def _animate_board(sgf: str) -> None:
    board = board_lib.Board()
    for i, (pt, player) in enumerate(loop_game(sgf)):
        os.system("clear")
        print(f"Move {i}")
        to_draw = board.copy()
        to_draw._grid[pt] = (
            Player.Spec1 if _triggering_move(pt) else Player.Spec2
        )
        print(to_draw.ascii_board())
        board.place(pt, player)
        time.sleep(3)


def read_game(fn):
    with open(fn, "rb") as f:
        bites = f.read()
    return bites.decode(encoding=chardet.detect(bites)["encoding"])


# _animate_board(read_game(os.path.join(consts.TOP_LEVEL_PATH, "data", "_data", _SAMPLE_FILE)))


def translate_files(src_dir, tgt_dir):
    BATCH_SIZE = 1000

    current_batch = list()
    batch_num = 0

    for file in glob.glob(os.path.join(src_dir, "*.sgf")):
        for datum in _get_data_from_sgf(read_game(file)):
            current_batch.append(datum.to_dict())
            if len(current_batch) >= BATCH_SIZE:
                # Dump
                landfill = os.path.join(tgt_dir, f"{batch_num}.pickle")
                with open(landfill, "wb") as f:
                    pickle.dump(current_batch, f)
                current_batch = list()
                batch_num += 1
    # Forget the rest of the data.


translate_files(
    src_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_data"),
    tgt_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_processed_data"),
)

