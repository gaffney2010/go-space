from typing import Dict, Optional, Set

from go_space import consts
from go_space.types import action, player, point


class Chonk(object):
    """Contains a set of contiguous stones"""

    def __init__(
        self,
        player: Optional[player.Player],
        points: Set[point.Point],
        liberties: Set[point.Point],
    ):
        self.player = player
        self.points = set()
        self.liberties = set()
        self._hash = 0
        if player == player.Player.Black:
            self._hash = 1

        for pt in points:
            self.add_point(pt)
        for pt in liberties:
            self.add_liberty(pt)

    @staticmethod
    def hash_point(point: point.Point) -> int:
        num = point.row * consts.SIZE + point.col
        return hash(num)

    def to_dict(self) -> Dict:
        assert self.__bool__()
        return {
            "player": self.player.value,
            "points": [p.to_dict() for p in self.points],
            "liberties": [p.to_dict() for p in self.liberties],
        }

    def __bool__(self):
        return self.player is not None

    def __hash__(self):
        return self._hash

    @staticmethod
    def from_dict(data: Dict) -> "Chonk":
        return Chonk(
            player=player.Player(data["player"]),
            points={point.Point.from_dict(p) for p in data["points"]},
            liberties={point.Point.from_dict(p) for p in data["liberties"]},
        )

    def add_liberty(self, point: point.Point) -> None:
        self.liberties.add(point)
        self._hash ^= 2 * self.hash_point(point)

    def remove_liberty(self, point: point.Point) -> action.Action:
        self.liberties.remove(point)
        self._hash ^= 2 * self.hash_point(point)
        if len(self.liberties) == 0:
            return action.Action.KILL
        return action.Action.ACK

    def add_point(self, point: point.Point) -> None:
        self.points.add(point)
        self._hash ^= 4 * self.hash_point(point)

    def remove_point(self, point: point.Point) -> None:
        self.points.remove(point)
        self._hash ^= 4 * self.hash_point(point)


NULL_CHUNK = Chonk(player=None, points=set(), liberties=set())
