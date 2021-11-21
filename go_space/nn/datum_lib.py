import json
from typing import Dict, Iterator

import numpy as np

from go_space import board_lib, consts, go_types


class Datum(object):
    def __init__(self, grid: go_types.Grid, next_pt: go_types.Point):
        self.next_pt = next_pt
        self.grid = grid.copy()
        self.grid.rotate(self._flip_x(), self._flip_y())
        self.grid.mask(self._iterator_corner())
        self.grid.resize(consts.DATA_BOARD_SIZE)

    def _flip_x(self) -> bool:
        half_board = consts.SIZE // 2 + 1
        c = self.next_pt.col
        return c > half_board

    def _flip_y(self) -> bool:
        half_board = consts.SIZE // 2 + 1
        r = self.next_pt.row
        return r > half_board

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
        result["grid"] = self.grid.to_sparse()
        result["next_pt"] = self.next_pt.to_dict()
        return result

    @staticmethod
    def _from_dict(data) -> "Datum":
        """Rebuild from one of the to_dict saved dicts."""
        return Datum(
            board=board_lib.Board.from_dict(data["board"]),
            next_pt=go_types.Point.from_dict(data["next_pt"]),
        )

    def to_json(self) -> str:
        return json.dumps(self._to_dict())

    @staticmethod
    def from_json(data_str) -> "Datum":
        return Datum._from_dict(json.loads(data_str))

    def np_feature(self) -> np.ndarray:
        raise NotImplementedError

    def np_target(self) -> np.ndarray:
        raise NotImplementedError
