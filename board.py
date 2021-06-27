"""Contains the Board class which is a board filled in with pieces,
representing either a tsumego problem or a game at a point in time."""

import enum
import json
from typing import Iterator, Dict, Optional

import attr

SIZE = 9  # This will be fixed for us


class PointFormatError(Exception):
    pass


@attr.s(frozen=True)
class Point(object):
    # By convention start counting from top-left
    row = attr.ib()  # Zero-indexed
    col = attr.ib()  # Zero-indexed

    @classmethod
    def fromLabel(cls, label: str) -> "Point":
        """Returns a Point from a label

        Arguments:
            label: May be in the format "A1" where "A" is the left-most column
                and "1" is the bottom-most row.  Or in the SGF format "aa" where
                the first letter is the left-most column, and the second letter
                is the top-most row.

        Returns:
            A Point class with the specified label.
        """
        first, second = label[0], label[1:]
        try:
            format = "A1"
            number = int(second)
        except:
            format = "SGF"

        if format == "A1":
            letter = first.upper()
            col = ord(letter) - ord("A")
            # Start from bottom with number=1 maps to SIZE-1
            row = SIZE - number
            return Point(row=row, col=col)
        if format == "SGF":
            first = first.lower()
            second = second.lower()
            col = ord(first) - ord("a")
            row = ord(second) - ord("a")
            return Point(row=row, col=col)
        raise PointFormatError("This should never happen")


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

    Returns:
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
