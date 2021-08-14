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

from typing import Iterator

import attr

from go_space import board

_SAMPLE_FILE = "1514127723010001630.sgf"


class SgfFormatError(board.FormatError):
    pass


def point_player_from_sgf(move_str: str) -> None:
    """Expect sgf_string to be like 'B[aa]'."""
    move_str = move_str.strip()
    if len(move_str) != 5:
        raise SgfFormatError
    
    if move_str[0] == 'B':
        # TODO: Consider moving some of these types.
        player = board.Player.Black
    elif move_str[0] == 'W':
        player = board.Player.White
    else:
        raise SgfFormatError

    return board.Point.fromLabel(move_str[2:4]), player


@attr.s
class Datum(object):
    board: board.Board = attr.ib()
    next_pt: board.Point = attr.ib()


def _triggering_move(point: board.Point) -> bool:
    r, c = point.mod_row_col()
    return r < 4 and c < 4


def _get_data_from_sgf(sgf: str) -> Iterator[Datum]:
    brd = board.Board()
    for move_str in sgf.split(";"):
        try:
            pt, player = point_player_from_sgf(move_str[:5])
        except board.FormatError:
            # Doesn't represent a move
            continue
        
        if _triggering_move(pt):
            yield Datum(board=brd.copy(), next_pt=pt)

        brd.place(pt, player)
