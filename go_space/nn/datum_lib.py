import json
from typing import Dict, Iterator

import numpy as np

from go_space import consts, go_types


class Datum(object):
    def __init__(self, grid: go_types.Grid, next_pt: go_types.Point):
        self.next_pt = next_pt
        self.grid = grid.copy()
        self.grid.rotate(self._flip_x(), self._flip_y())
        # Rotate pt also:
        r, c = next_pt.mod_row_col()
        self.next_pt = go_types.Point(r, c)
        self.grid.mask(self._iterator_corner())
        self.grid.resize(consts.DATA_BOARD_SIZE)

    def _flip_x(self) -> bool:
        half_board = consts.SIZE // 2 + 1
        r = self.next_pt.row
        return r > half_board

    def _flip_y(self) -> bool:
        half_board = consts.SIZE // 2 + 1
        c = self.next_pt.col
        return c > half_board

    def _iterator_corner(self) -> Iterator[go_types.Point]:
        """Sweeps through

        # xxxxxxxx.
        # xxxxxxxx.
        # xxxxxxxx.
        # xxxxxxxx.
        # xxxxxx...
        # xxxxx....
        # xxxx.....
        # xxxx.....
        # .........

        in the corner as next_pt
        """
        x, y, dx, dy = 0, 0, 1, 1

        offsets = (
            [(0, i) for i in range(8)]
            + [(1, i) for i in range(8)]
            + [(2, i) for i in range(8)]
            + [(3, i) for i in range(8)]
            + [(4, i) for i in range(6)]
            + [(5, i) for i in range(5)]
            + [(6, i) for i in range(4)]
            + [(7, i) for i in range(4)]
        )

        for a, b in offsets:
            yield go_types.Point(row=x + a * dx, col=y + b * dy)

    def _to_dict(self) -> Dict:
        """Should contain all the info needed to reconstruct."""
        result = dict()
        result["grid"] = self.grid.to_dict()
        result["next_pt"] = self.next_pt.to_dict()
        return result

    @staticmethod
    def _from_dict(data) -> "Datum":
        """Rebuild from one of the to_dict saved dicts."""
        return Datum(
            grid=go_types.Grid.from_dict(data["grid"]),
            next_pt=go_types.Point.from_dict(data["next_pt"]),
        )

    def to_json(self) -> str:
        return json.dumps(self._to_dict())

    def data_size(self) -> int:
        result = 0
        for pt in self._iterator_corner():
            if self.grid[pt]:
                result += 1
        return result

    @staticmethod
    def from_json(data_str) -> "Datum":
        return Datum._from_dict(json.loads(data_str))

    def np_feature(self) -> np.ndarray:
        # Add dimension for single "channel"
        result = np.zeros([consts.DATA_BOARD_SIZE, consts.DATA_BOARD_SIZE, 1])
        for r in range(consts.DATA_BOARD_SIZE):
            for c in range(consts.DATA_BOARD_SIZE):
                if chonk := self.grid[go_types.Point(row=r, col=c)]:
                    result[r, c, 0] = 1 if chonk.player == go_types.Player.Black else -1
        return result

    def np_target(self) -> np.ndarray:
        # TODO: Magic numbers
        result = [0] * 16
        r, c = self.next_pt.row, self.next_pt.col
        result[4*r+c] = 1
        return result
