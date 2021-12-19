import attr
import numpy as np

from . import grid_lib


@attr.s
class Tseumego(object):
    file_name: str = attr.ib()
    grid: grid_lib.Grid = attr.ib()
    embedding: np.ndarray = attr.ib()
