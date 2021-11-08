"""Contains the Board class which is a board filled in with pieces,
representing either a tsumego problem or a game at a point in time."""

from typing import Iterator, Dict, List, Optional, Set

from go_space import consts
from go_space.types import *


def all_points() -> Iterator[Point]:
    """Loops through all the points on the board."""
    for i in range(consts.SIZE):
        for j in range(consts.SIZE):
            yield Point(row=i, col=j)


def _adj_points(point: Point) -> Iterator[Point]:
    for drow, dcol in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        row, col = point.row + drow, point.col + dcol
        if 0 <= row < consts.SIZE and 0 <= col < consts.SIZE:
            yield Point(row, col)


class GoError(Exception):
    """Errors relating to the way that go is played."""

    pass


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
    def __init__(self):
        self._grid: Dict[Point, Optional[Chonk]] = dict()

    def __setitem__(self, key: Point, value: Optional[Chonk]) -> None:
        assert(isinstance(key, Point))
        self._grid[key] = value

    def __getitem__(self, key: Point) -> Optional[Chonk]:
        return self._grid[key]

    def __contains__(self, key: Point) -> bool:
        return key in self._grid

    def items(self) -> Iterator[Tuple[Point, Optional[Chonk]]]:
        for k, v in self._grid.items():
            yield k, v


class Board(object):
    def __init__(self):
        self._grid = Grid()
        for point in all_points():
            # No pieces placed yet
            self._grid[point] = NULL_CHUNK

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
            if not chonk:
                # This is still NULL_CHUNK
                continue
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
        for k, v in data["grid"].items():
            result._grid[Point.from_dict(k)] = chonks[v]
        return result

    def copy(self) -> "Board":
        """Deep copies"""
        return Board.from_dict(self.to_dict())

    def place(self, point: Point, player: Player) -> None:
        if point not in self._grid:
            raise GoError("Tried to place out of bounds")
        if self._grid[point].player:
            raise GoError("Tried to put piece on piece")

        my_chonks = set()
        their_chonks = set()
        liberties = set()
        for pt in _adj_points(point):
            if self._grid[pt].player == player:
                my_chonks.add(self._grid[pt])
            elif self._grid[pt].player == other_player(player):
                their_chonks.add(self._grid[pt])
            elif self._grid[pt].player is None:
                liberties.add(pt)
            else:
                raise FormatError
        new_chonk = Chonk(player=player, points={point}, liberties=liberties)
        my_chonks.add(new_chonk)
        
        # Combine chonks
        combined_points = set()
        combined_liberties = set()
        for chonk in my_chonks:
            combined_points |= chonk.points
            combined_liberties |= chonk.liberties
        if point in combined_liberties:
            combined_liberties.remove(point)
        combined_chonk = Chonk(player=player, points=combined_points, liberties=combined_liberties)
        for pt in combined_points:
            self._grid[pt] = combined_chonk

        # Reduce liberties of opponent.
        for chonk in their_chonks:
            if chonk.remove_liberty(point) == Action.KILL:
                # First remove the stones
                for pt in chonk.points:
                    self._grid[pt] = NULL_CHUNK
                # Then check if any chonks need a new liberty
                for pt in chonk.points:
                    adj_chonks = set()
                    for adj_pt in _adj_points(pt):
                        if adj_chonk := self._grid[adj_pt]:
                            adj_chonks.add(adj_chonk)
                    for chonk in adj_chonks:
                        chonk.add_liberty(pt)

    def stones(self) -> Iterator[Stone]:
        """Loop through all stones."""
        for point, chonk in self._grid.items():
            if chonk.player:
                yield Stone(point=point, player=chonk.player)

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
                piece = self._grid[Point(row=r, col=c)].player
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
