"""Contains the Board class which is a board filled in with pieces,
representing either a tsumego problem or a game at a point in time."""

import enum
import json
from typing import Iterator, Dict, Optional

import attr

SIZE = 9  # This will be fixed for us


@attr.s(frozen=True)
class Point(object):
    # By convention start counting from bottom-left
    row = attr.ib()  # Zero-indexed
    col = attr.ib()  # Zero-indexed

    @classmethod
    def fromLabel(cls, label: str) -> "Point":
        """Returns a Point from an 'A1'-style human-label."""
        letter, number = label[0].upper(), int(label[1:])
        col = ord(letter) - ord("A")
        row = number - 1  # To zero-index
        return Point(row=row, col=col)


def all_points() -> Iterator[Point]:
    """Loops through all the points on the board."""
    for i in range(SIZE):
        for j in range(SIZE):
            yield Point(row=i, col=j)


class Player(enum.Enum):
    Black = 1
    White = 2


class GoError(Exception):
    """Errors relating to the way that go is played."""

    pass


class Board(object):
    def __init__(self):
        self._grid: Dict[Point, Optional[Player]] = dict()
        for point in all_points():
            # No pieces placed yet
            self._grid[point] = None

    def place(self, point: Point, player: Player):
        if point not in self._grid:
            raise GoError("Tried to place out of bounds")
        if self._grid[point] is not None:
            raise GoError("Tried to put piece on piece")

        self._grid[point] = player


class MalformedJsonError(Exception):
    pass


def boardFromJson(json_str: str) -> Board:
    """Creates a board from a json

    Arguments:
        json_str: A json

    returns:
        A board that has only the specified black and white pieces.
    """
    parsed = json.loads(json_str)

    MUST_CONTAIN_FIELDS = ("blacks", "whites")
    for field in MUST_CONTAIN_FIELDS:
        if field not in parsed:
            raise MalformedJsonError(f"json missing field = {field}")

    result = Board()

    for point_str in parsed["blacks"]:
        result.place(point=Point.fromLabel(point_str), player=Player.Black)
    for point_str in parsed["whites"]:
        result.place(point=Point.fromLabel(point_str), player=Player.White)

    return result
