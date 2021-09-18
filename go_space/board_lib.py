"""Contains the Board class which is a board filled in with pieces,
representing either a tsumego problem or a game at a point in time."""

import copy
from typing import FrozenSet, Iterator, Dict, List, Optional

from go_space import consts
from go_space.types import *


def all_points() -> Iterator[Point]:
    """Loops through all the points on the board."""
    for i in range(consts.SIZE):
        for j in range(consts.SIZE):
            yield Point(row=i, col=j)


class GoError(Exception):
    """Errors relating to the way that go is played."""

    pass


@attr.s(frozen=True)
class Chonk(object):
    """Contains a set of contiguous stones"""
    player: Player = attr.ib()
    points: FrozenSet[Point] = attr.ib()
    liberties: FrozenSet[Point] = attr.ib()

    def to_dict(self) -> Dict:
        return {
            "player": self.player.value,
            "points": (p.to_dict() for p in self.points),
            "liberties": (p.to_dict() for p in self.liberties)
        }

    @staticmethod
    def from_dict(self, data: Dict) -> "Chonk":
        return Chonk(
            player=Player(data["player"]),
            points=frozenset((Point.from_dict(p) for p in data["points"])),
            liberties=frozenset((Point.from_dict(p) for p in data["liberties"])),
        )


class Board(object):
    def __init__(self):
        self._grid: Dict[Point, Optional[Player]] = dict()
        for point in all_points():
            # No pieces placed yet
            self._grid[point] = None

    def to_dict(self) -> Dict:
        """Should contain all the info needed to reconstruct."""
        # Because many points will point to the same chonk, we try to not repeat
        result = dict()
        result["chonks"] = list()
        result["grid"] = dict()

        chonk_dict = dict()
        chonk_id = 0
        # Index for result["chonks"] gets stored to point in "grid"
        for point, chonk in self._grid.items():
            if chonk not in chonk_dict:
                chonk_dict[chonk] = chonk_id; chonk_id += 1
                result["chonks"].append(chonk.to_dict())
            result["grid"][point.to_dict()] = chonk_dict[chonk]

        return result

    @staticmethod
    def from_dict(data: Dict) -> "Board":
        """Rebuild from one of the to_dict saved dicts."""
        # First build all the chonks
        chonks = [Chonk.from_dict(ch) for ch in data["chonks"]]

        result = Board()
        result._grid = {k: chonks[v] for k, v in data["grid"].items()}
        return result

    def copy(self) -> "Board":
        """Deep copies"""
        return Board.from_dict(self.to_dict())

    def place(self, point: Point, player: Player) -> None:
        if point not in self._grid:
            raise GoError("Tried to place out of bounds")
        if self._grid[point] is not None:
            raise GoError("Tried to put piece on piece")

        self._grid[point] = player

    def stones(self) -> Iterator[Stone]:
        """Loop through all stones."""
        for point, player in self._grid.items():
            if player is not None:
                yield Stone(point=point, player=player)

    def ascii_board(self) -> str:
        """Returns ASCII art for board"""
        def stone_char(stone: Optional[Player]) -> str:
            STONE_CHAR = {
                Player.Black: "#",
                Player.White: "O",
                Player.Spec1: "?",
                Player.Spec2: "!",
            }
            BLANK_CHAR = '.'
            return STONE_CHAR.get(stone, BLANK_CHAR)

        result_rows = list()
        for r in range(consts.SIZE):
            row = list()
            for c in range(consts.SIZE):
                piece = self._grid[Point(row=r, col=c)]
                row.append(stone_char(piece))
            result_rows.append("".join(row))
        return "\n".join(result_rows)


class MalformedJsonError(Exception):
    pass


# BlackWhite board strings as read from JSON files in classes dir.
BwBoardStr = Dict[str, List[str]]

def boardFromBwBoardStr(bw: BwBoardStr) -> Board:
    """Creates a board from a parsed json

    Arguments:
        bw: A dict with keys being "black" and "white" and values being lists of
            strings representing places where stones of that color are placed.

            For example, {"black": {"aa", "ab"}, "white": {"bb"}} would place
            two black stones in positions "aa" and "ab" and one white stone in
            position "bb".

            These are SGF-style position names.  See Point.fromLabel for
            acceptable format.

    Returns:
        A board that has only the specified black and white pieces.
    """
    MUST_CONTAIN_FIELDS = ("black", "white")
    for field in MUST_CONTAIN_FIELDS:
        if field not in bw:
            raise MalformedJsonError(f"json missing field = {field}")

    result = Board()

    for point_str in bw["black"]:
        result.place(point=Point.fromLabel(point_str), player=Player.Black)
    for point_str in bw["white"]:
        result.place(point=Point.fromLabel(point_str), player=Player.White)

    return result
