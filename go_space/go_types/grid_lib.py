from typing import Dict, Iterator, List, Optional, Tuple

from go_space import consts

from . import chonk_lib, player_lib, point_lib


def _all_points(size: int) -> Iterator[point_lib.Point]:
    """Loops through all the points on the board."""
    for i in range(size):
        for j in range(size):
            yield point_lib.Point(row=i, col=j)


class Grid(object):
    def _clear(self):
        """Fills in NULL_CHUNK.  Clear or initialize."""
        for point in _all_points(self.size):
            # No pieces placed yet
            self._grid[point] = chonk_lib.NULL_CHUNK

    def __init__(self, size: int = consts.SIZE):
        self.size = size
        self._grid: Dict[point_lib.Point, Optional[chonk_lib.Chonk]] = dict()
        self._clear()

    def __setitem__(
        self, key: point_lib.Point, value: Optional[chonk_lib.Chonk]
    ) -> None:
        assert isinstance(key, point_lib.Point)
        self._grid[key] = value

    def __getitem__(self, key: point_lib.Point) -> Optional[chonk_lib.Chonk]:
        return self._grid[key]

    def __contains__(self, key: point_lib.Point) -> bool:
        return key in self._grid

    def _copy_grid(self) -> Dict[point_lib.Point, Optional[chonk_lib.Chonk]]:
        return {k: v for k, v in self.items()}

    def rotate(self, flip_x: bool, flip_y: bool) -> None:
        x, y, dx, dy = 0, 0, 1, 1
        if flip_x:
            x, dx = self.size - 1, -1
        if flip_y:
            y, dy = self.size - 1, -1

        grid_copy = self._copy_grid()
        for i in range(self.size):
            for j in range(self.size):
                to_point = point_lib.Point(i, j)
                from_point = point_lib.Point(x + i * dx, y + j * dy)
                self[to_point] = grid_copy[from_point]

    def mask(self, points: Iterator[point_lib.Point]) -> None:
        """Remove all points except those passed"""
        grid_copy = self._copy_grid()
        self._clear()
        for point in points:
            self[point] = grid_copy[point]

    def resize(self, size: int) -> None:
        grid_copy = self._copy_grid()
        self.grid = dict()
        self.size = size
        self._clear()

        for point in _all_points(self.size):
            self[point] = grid_copy[point]

    def items(self) -> Iterator[Tuple[point_lib.Point, Optional[chonk_lib.Chonk]]]:
        for k, v in self._grid.items():
            yield k, v

    def to_dict(self) -> Dict:
        result = dict()
        result["size"] = self.size
        result["sparse_grid"] = list()
        for point in _all_points(self.size):
            if chonk := self.__getitem__(point):
                result["sparse_grid"].append((point, chonk.player))

    def copy(self) -> "Grid":
        """Deep copy."""
        result = Grid(size=self.size)
        result._grid = self._copy_grid()
        return result

    @staticmethod
    def from_dict(data_dict: Dict) -> "Grid":
        result = Grid(data_dict["size"])
        for player, point in data_dict["sparse_grid"]:
            result[player] = point
        return result
