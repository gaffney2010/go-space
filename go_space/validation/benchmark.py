"""Computes Buhlmann credibility on some informationless embeddings."""

from go_space import embeddings
from go_space.validation import buhlmann


if __name__ == "__main__":
    nn_embed = embeddings.NNEmbed()

    # We found that random scores drop quickly until ~40, then level out.
    for d in range(10, 110, 10):
        print("=================")
        print(f"Random embedding (dim {d}):")
        print(buhlmann.computeBuhlmannOnClasses(embeddings.make_random_embedding(d)))
        print()

    print("=================")
    print("Dumb embedding:")
    print(buhlmann.computeBuhlmannOnClasses(embeddings.dumb_embedding))
    print()

    print("==================")
    print("NN embedding:")
    print(buhlmann.computeBuhlmannOnClasses(nn_embed.nn_embedding))
    print()
