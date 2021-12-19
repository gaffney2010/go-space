import os
import pickle
import random

import numpy as np

from go_space import consts
# TODO: Better way to do this.
# Needed for the pickle.
from go_space.go_types.tseumego_lib import Tseumego


with open(
    os.path.join(consts.TOP_LEVEL_PATH, "data", "_pickled_tseumego", "basics.pickle"),
    "rb",
) as f:
    tseumegos = pickle.load(f)
num = len(tseumegos)

similarity = np.zeros([num, num])
for i in range(num):
    for j in range(num):
        xi, xj = tseumegos[i].embedding, tseumegos[j].embedding
        similarity[i, j] = np.dot(xi, xj) / np.sqrt(np.dot(xi, xi) * np.dot(xj, xj))

action = "d"
while action != "e":
    if action == "d":
        ind = random.randrange(num)
        grid = tseumegos[ind].grid
    if action == "n":
        best_score = -1
        best_i = None
        for i in range(num):
            if i == ind:
                continue
            if similarity[i, ind] > best_score:
                best_score = similarity[i, ind]
                best_i = i
        ind = best_i
        grid = tseumegos[ind].grid

    print(grid.ascii_board())

    print("Type 'd' for new board, 'n' for neighbor, or 'e' to exit.")
    action = input()

print("")
print("Good bye")
