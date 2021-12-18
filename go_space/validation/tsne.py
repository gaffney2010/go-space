import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.manifold import TSNE

from go_space import board_lib, consts, embeddings


classes_folder = os.path.join(consts.TOP_LEVEL_PATH, "validation", "classes")

nn_embed = embeddings.NNEmbed()
embed_func = nn_embed.nn_embedding

X_, y_ = list(), list()
for file in os.listdir(classes_folder):
    rel_path = os.path.join(classes_folder, file)
    with open(rel_path, "r") as f:
        raw_json = f.read()
    clss = json.loads(raw_json)
    for brd in clss["boards"]:
        this_board = board_lib.boardFromBwBoardStr(brd)
        X_.append(embed_func(this_board))
        y_.append(file.split(".")[0])


X = np.stack(X_, axis=0)
y = np.stack(y_, axis=0)

tsne = TSNE(2)
tsne_result = tsne.fit_transform(X)

tsne_result_df = pd.DataFrame(
    {"tsne_1": tsne_result[:, 0], "tsne_2": tsne_result[:, 1], "label": y}
)
fig, ax = plt.subplots(1)
sns.scatterplot(x="tsne_1", y="tsne_2", hue="label", data=tsne_result_df)
lim = (tsne_result.min() - 50, tsne_result.max() + 50)
ax.set_xlim(lim)
ax.set_ylim(lim)
ax.set_aspect("equal")
ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

plt.savefig("tsne.png")
