# TODO: Break this file up.  One file per class.

import enum
from typing import Dict, Iterator, List, Optional, Set, Tuple

import attr

from go_space import consts


class FormatError(Exception):
    pass


class PointFormatError(FormatError):
    pass


@attr.s(frozen=True)
class Point(object):
    # By convention start counting from top-left
    row: int = attr.ib()  # Zero-indexed
    col: int = attr.ib()  # Zero-indexed

    # TODO: Change name of to/from_dict everywhere.
    # Despite being called `to_dict`, we prefer a tuple cast, since the object is immutable.
    def to_dict(self) -> Tuple[int]:
        """Should contain all the info needed to reconstruct."""
        return (self.row, self.col)

    @staticmethod
    def from_dict(data: Tuple[int]) -> "Point":
        """Rebuild from one of the to_dict saved dicts."""
        return Point(row=data[0], col=data[1])

    def neighbors(self) -> Iterator["Point"]:
        if self.row - 1 >= 0:
            yield Point(row=self.row-1, col=self.col)
        if self.row + 1 < consts.SIZE:
            yield Point(row=self.row+1, col=self.col)
        if self.col - 1 >= 0:
            yield Point(row=self.row, col=self.col-1)
        if self.col + 1 < consts.SIZE:
            yield Point(row=self.row, col=self.col+1)

    def mod_row_col(self) -> Tuple[int, int]:
        """Gives coordinates after rotating to get point in low-index quarter."""
        half_board = consts.SIZE // 2 + 1
        r, c = self.row, self.col

        if r >= half_board:
            r = consts.SIZE - 1 - r
        if c >= half_board:
            c = consts.SIZE - 1 - c

        return r, c

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
            # Start from bottom with number=1 maps to consts.SIZE-1
            row = consts.SIZE - number
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
    for i in range(consts.SIZE):
        for j in range(consts.SIZE):
            yield Point(row=i, col=j)


class Player(enum.Enum):
    Black = 1
    White = 2
    # Special "Players" for debugging
    Spec1 = 3
    Spec2 = 4


def other_player(player: Player) -> Player:
    if player == Player.Black:
        return Player.White
    if player == Player.White:
        return Player.Black
    raise FormatError


@attr.s(frozen=True)
class Stone(object):
    point: Point = attr.ib()
    player: Player = attr.ib()


class Action(enum.Enum):
    ACK = 1
    # Should remove this chonk now, it's dead.
    KILL = 2


class Chonk(object):
    """Contains a set of contiguous stones"""
    def __init__(self, player: Optional[Player], points: Set[Point], liberties: Set[Point]):
        self.player = player
        self.points = set()
        self.liberties = set()
        self._hash = 0
        if player == Player.Black:
            self._hash = 1

        for pt in points:
            self.add_point(pt)
        for pt in liberties:
            self.add_liberty(pt)

    @staticmethod
    def hash_point(point: Point) -> int:
        num = point.row * consts.SIZE + point.col
        return hash(num)

    def to_dict(self) -> Dict:
        assert(self.__bool__())
        return {
            "player": self.player.value,
            "points": [p.to_dict() for p in self.points],
            "liberties": [p.to_dict() for p in self.liberties]
        }

    def __bool__(self):
        return self.player is not None

    def __hash__(self):
        return self._hash

    @staticmethod
    def from_dict(data: Dict) -> "Chonk":
        return Chonk(
            player=Player(data["player"]),
            points={Point.from_dict(p) for p in data["points"]},
            liberties={Point.from_dict(p) for p in data["liberties"]},
        )

    def add_liberty(self, point: Point) -> None:
        self.liberties.add(point)
        self._hash ^= 2 * self.hash_point(point)
    
    def remove_liberty(self, point: Point) -> Action:
        self.liberties.remove(point)
        self._hash ^= 2 * self.hash_point(point)
        if len(self.liberties) == 0:
            return Action.KILL
        return Action.ACK

    def add_point(self, point: Point) -> None:
        self.points.add(point)
        self._hash ^= 4 * self.hash_point(point)

    def remove_point(self, point: Point) -> None:
        self.points.remove(point)
        self._hash ^= 4 * self.hash_point(point)


NULL_CHUNK = Chonk(player=None, points=set(), liberties=set())


class Grid(object):
    @staticmethod
    def _clear(grid_dict):
        for point in all_points():
            # No pieces placed yet
            grid_dict[point] = NULL_CHUNK

    def __init__(self):
        self._grid: Dict[Point, Optional[Chonk]] = dict()
        Grid._clear(self._grid)

    def __setitem__(self, key: Point, value: Optional[Chonk]) -> None:
        assert(isinstance(key, Point))
        self._grid[key] = value

    def __getitem__(self, key: Point) -> Optional[Chonk]:
        return self._grid[key]

    def __contains__(self, key: Point) -> bool:
        return key in self._grid

    def mask(self, points: Iterator[Point]) -> None:
        """Remove all points except those passed"""
        new_grid = dict()
        Grid._clear(new_grid)
        for point in points:
            new_grid[point] = self.__getitem__(point)
        # Happens to deep copy self._grid
        self._grid = new_grid

    def items(self) -> Iterator[Tuple[Point, Optional[Chonk]]]:
        for k, v in self._grid.items():
            yield k, 
            
    def to_sparse(self) -> List[Tuple[Point, Player]]:
        result = list()
        for point in all_points():
            if chonk := self.__getitem__(point):
                result.append((point, chonk.player))

    def copy(self) -> "Grid":
        # TODO: Make this path clearer.
        """Shallow copy.  Deep copy when run with mask."""
        result = Grid()
        result._grid = self._grid
        return result

    @staticmethod
    def from_sparse(sparse: List[Tuple[Point, Player]]) -> "Grid":
        result = Grid()
        for player, point in sparse:
            result[player] = point
        return result
