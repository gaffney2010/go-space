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
import pickle
import time
from typing import Dict, Iterator, Tuple

import chardet

from go_space import board_lib, consts, exceptions
from go_space.go_types import *

_SAMPLE_FILE = "1514127723010001630.sgf"

_DATA_SIZE = 11


class SgfFormatError(exceptions.FormatError):
    pass


# TODO: Delete a bunch of unused to_dict/from_dict functions.

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


class Datum(object):
    def __init__(self, grid: Grid, next_pt: Point):
        self.next_pt = next_pt
        self.grid = grid.copy()
        self.grid.rotate(self._flip_x(), self._flip_y())
        self.grid.mask(self._iterator_corner())
        self.grid.resize(_DATA_SIZE)

    def _flip_x(self) -> bool:
        half_board = consts.SIZE // 2 + 1
        c = self.next_pt.col
        return c > half_board

    def _flip_y(self) -> bool:
        half_board = consts.SIZE // 2 + 1
        r = self.next_pt.row
        return r > half_board

    def _iterator_corner(self) -> Iterator[Point]:
        """Sweeps through

        # xxxxxxxx.
        # xxxxxxxx.
        # xxxxxxxx.
        # xxxxxxxx.
        # xxxxxx...
        # xxxxx....
        # xxxx.....
        # xxxx.....
        # .........

        in the corner as next_pt
        """
        x, y, dx, dy = 0, 0, 1, 1

        offsets = (
            [(0, i) for i in range(8)]
            + [(1, i) for i in range(8)]
            + [(2, i) for i in range(8)]
            + [(3, i) for i in range(8)]
            + [(4, i) for i in range(6)]
            + [(5, i) for i in range(5)]
            + [(6, i) for i in range(4)]
            + [(7, i) for i in range(4)]
        )

        for a, b in offsets:
            yield Point(row=x + a * dx, col=y + b * dy)

    def to_dict(self) -> Dict:
        """Should contain all the info needed to reconstruct."""
        result = dict()
        result["grid"] = self.grid.to_sparse()
        result["next_pt"] = self.next_pt.to_dict()
        return result

    @staticmethod
    def from_dict(data) -> "Datum":
        """Rebuild from one of the to_dict saved dicts."""
        return Datum(
            board=board_lib.Board.from_dict(data["board"]),
            next_pt=Point.from_dict(data["next_pt"]),
        )


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


def _animate_board(sgf: str) -> None:
    board = board_lib.Board()
    for i, (pt, player) in enumerate(loop_game(sgf)):
        os.system("clear")
        print(f"Move {i}")
        to_draw = board.copy()
        to_draw._grid[pt] = Player.Spec1 if _triggering_move(pt) else Player.Spec2
        print(to_draw.ascii_board())
        board.place(pt, player)
        time.sleep(3)


def read_game(fn):
    with open(fn, "rb") as f:
        bites = f.read()
    return bites.decode(encoding=chardet.detect(bites)["encoding"])


# _animate_board(read_game(os.path.join(consts.TOP_LEVEL_PATH, "data", "_data", _SAMPLE_FILE)))


# TODO: Just save 40k points total, single file.
# TODO: Save test/train target/features
def translate_files(src_dir, tgt_dir):
    BATCH_SIZE = 1000

    current_batch = list()
    batch_num = 0

    # !!!!!!!!!!!!!!!!!!!!!
    # When a board breaks, save it to a file as a special case.

    for file in glob.glob(os.path.join(src_dir, "*.sgf")):
        for datum in _get_data_from_sgf(read_game(file)):
            if batch_num >= 1000:
                # To avoid blowing up my hard drive
                assert False

            current_batch.append(datum.to_dict())
            if len(current_batch) >= BATCH_SIZE:
                # Dump
                print(f"Working on pickle dump #{batch_num}")
                landfill = os.path.join(tgt_dir, f"{batch_num}.pickle")
                with open(landfill, "wb") as f:
                    pickle.dump(current_batch, f)
                current_batch = list()
                batch_num += 1


translate_files(
    src_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_data"),
    tgt_dir=os.path.join(consts.TOP_LEVEL_PATH, "data", "_processed_data"),
)
