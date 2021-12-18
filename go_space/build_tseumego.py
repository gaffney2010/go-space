"""These are unclassified problems.  We embed and look at them individually.
"""

import os

import attr
import numpy as np

from go_space import consts, embeddings
from go_space.go_types import grid_lib


@attr.s
class Tseumego(object):
    file_name: str = attr.ib()
    grid: grid_lib.Grid = attr.ib()
    embedding: np.ndarray = attr.ib()


embedding_func = embeddings.nn_embedding


print("Start")
all_files = list()
for root, dirs, files in os.walk(
    os.path.join(consts.TOP_LEVEL_PATH, "data", "_tseumego_problems")
):
    for file in files:
        all_files.append(os.path.join(root, file))
print(all_files[::100])
print("End")
