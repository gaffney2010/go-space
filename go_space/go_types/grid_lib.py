from typing import Dict, Iterator, List, Optional, Tuple

from go_space import consts
from . import chonk_lib, player_lib, point_lib


def _all_points() -> Iterator[point_lib.Point]:
    """Loops through all the points on the board."""
    for i in range(consts.SIZE):
        for j in range(consts.SIZE):
            yield point_lib.Point(row=i, col=j)


class Grid(object):
    @staticmethod
    def _clear(grid_dict):
        for point in _all_points():
            # No pieces placed yet
            grid_dict[point] = chonk_lib.NULL_CHUNK

    def __init__(self):
        self._grid: Dict[point_lib.Point, Optional[chonk_lib.Chonk]] = dict()
        Grid._clear(self._grid)

    def __setitem__(self, key: point_lib.Point, value: Optional[chonk_lib.Chonk]) -> None:
        assert isinstance(key, point_lib.Point)
        self._grid[key] = value

    def __getitem__(self, key: point_lib.Point) -> Optional[chonk_lib.Chonk]:
        return self._grid[key]

    def __contains__(self, key: point_lib.Point) -> bool:
        return key in self._grid

    def mask(self, points: Iterator[point_lib.Point]) -> None:
        """Remove all points except those passed"""
        new_grid = dict()
        Grid._clear(new_grid)
        for point in points:
            new_grid[point] = self.__getitem__(point)
        # Happens to deep copy self._grid
        self._grid = new_grid

    def items(self) -> Iterator[Tuple[point_lib.Point, Optional[chonk_lib.Chonk]]]:
        for k, v in self._grid.items():
            yield k,

    def to_sparse(self) -> List[Tuple[point_lib.Point, player_lib.Player]]:
        result = list()
        for point in _all_points():
            if chonk := self.__getitem__(point):
                result.append((point, chonk.player))

    def copy(self) -> "Grid":
        # TODO: Make this path clearer.
        """Shallow copy.  Deep copy when run with mask."""
        result = Grid()
        result._grid = self._grid
        return result

    @staticmethod
    def from_sparse(sparse: List[Tuple[point_lib.Point, player_lib.Player]]) -> "Grid":
        result = Grid()
        for player, point in sparse:
            result[player] = point
        return result
