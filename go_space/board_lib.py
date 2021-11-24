"""Contains the Board class which is a board filled in with pieces,
representing either a tsumego problem or a game at a point in time."""

from typing import Iterator, Dict, List, Optional

from go_space import consts, exceptions, go_types


def _adj_points(point: go_types.Point) -> Iterator[go_types.Point]:
    for drow, dcol in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        row, col = point.row + drow, point.col + dcol
        if 0 <= row < consts.SIZE and 0 <= col < consts.SIZE:
            yield go_types.Point(row, col)


class GoError(Exception):
    """Errors relating to the way that go is played."""

    pass


def _other_player(player: go_types.Player) -> go_types.Player:
    if player == go_types.Player.Black:
        return go_types.Player.White
    if player == go_types.Player.White:
        return go_types.Player.Black
    raise exceptions.FormatError


class Board(object):
    def __init__(self):
        self._grid = go_types.Grid()

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
                chonk_dict[chonk] = chonk_id
                chonk_id += 1
                result["chonks"].append(chonk.to_dict())
            result["grid"][point.to_dict()] = chonk_dict[chonk]

        return result

    @staticmethod
    def from_dict(data: Dict) -> "Board":
        """Rebuild from one of the to_dict saved dicts."""
        # First build all the chonks
        chonks = [go_types.Chonk.from_dict(ch) for ch in data["chonks"]]

        result = Board()
        for k, v in data["grid"].items():
            result._grid[go_types.Point.from_dict(k)] = chonks[v]
        return result

    def copy(self) -> "Board":
        """Deep copies"""
        return Board.from_dict(self.to_dict())

    def place(self, point: go_types.Point, player: go_types.Player) -> None:
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
            elif self._grid[pt].player == _other_player(player):
                their_chonks.add(self._grid[pt])
            elif self._grid[pt].player is None:
                liberties.add(pt)
            else:
                raise exceptions.FormatError
        new_chonk = go_types.Chonk(player=player, points={point}, liberties=liberties)
        my_chonks.add(new_chonk)

        # Combine chonks
        combined_points = set()
        combined_liberties = set()
        for chonk in my_chonks:
            combined_points |= chonk.points
            combined_liberties |= chonk.liberties
        if point in combined_liberties:
            combined_liberties.remove(point)
        combined_chonk = go_types.Chonk(
            player=player, points=combined_points, liberties=combined_liberties
        )
        for pt in combined_points:
            self._grid[pt] = combined_chonk

        # Reduce liberties of opponent.
        for chonk in their_chonks:
            if chonk.remove_liberty(point) == go_types.Action.KILL:
                # First remove the stones
                for pt in chonk.points:
                    self._grid[pt] = go_types.NULL_CHUNK
                # Then check if any chonks need a new liberty
                for pt in chonk.points:
                    adj_chonks = set()
                    for adj_pt in _adj_points(pt):
                        if adj_chonk := self._grid[adj_pt]:
                            adj_chonks.add(adj_chonk)
                    for chonk in adj_chonks:
                        chonk.add_liberty(pt)

    def stones(self) -> Iterator[go_types.Stone]:
        """Loop through all stones."""
        for point, chonk in self._grid.items():
            if chonk.player:
                yield go_types.Stone(point=point, player=chonk.player)

    def ascii_board(self) -> str:
        """Returns ASCII art for board"""
        return self._grid.ascii_board()


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
        result.place(
            point=go_types.Point.fromLabel(point_str), player=go_types.Player.Black
        )
    for point_str in bw["white"]:
        result.place(
            point=go_types.Point.fromLabel(point_str), player=go_types.Player.White
        )

    return result
