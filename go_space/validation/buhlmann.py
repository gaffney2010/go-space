"""Contains a function to score an embedding.

Embeddings are score with Buhlmann credibility.  A smaller number is better."""

import json
import os
from typing import Callable, List

import attr
import numpy as np

from go_space import board, consts


# Must be a constant dimension
Embedding = Callable[[board.Board], np.ndarray]


@attr.s
class Moments(object):
    mean: np.ndarray = attr.ib()
    var: float = attr.ib()


def _momentsFromPoints(points: List[np.ndarray]) -> Moments:
    mean = np.average(points, axis=0)
    var = 0
    for point in points:
        # Loop through dimensions
        for i, di in enumerate(point):
            var += (di - mean[i]) ** 2
    var /= len(points)

    return Moments(mean=mean, var=var)


def classMoments(embedding: Embedding, clss: List[board.BwBoardStr]) -> Moments:
    points = list()
    for brd in clss:
        this_board = board.boardFromBwBoardStr(brd)
        points.append(embedding(this_board))

    return _momentsFromPoints(points)


def buhlmannCredibility(moments: List[Moments]):
    epv = np.average([m.var for m in moments])
    vhm = _momentsFromPoints([m.mean for m in moments]).var

    return epv/vhm


def computeBuhlmannOnClasses(embedding: Embedding):
    """Loops through classes folder and calculates Buhlmann on these data"""
    classes_folder = os.path.join(consts.TOP_LEVEL_PATH, "validation", "classes")

    all_moments = list()
    for file in os.listdir(classes_folder):
        rel_path = os.path.join(classes_folder, file)
        with open(rel_path, "r") as f:
            raw_json = f.read()
        clss = json.loads(raw_json)
        all_moments.append(classMoments(embedding, clss["boards"]))

    return buhlmannCredibility(all_moments)
