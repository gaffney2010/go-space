"""Prints all the boards in a class.  Used for debugging."""

import json
import os

import argparse

import board
import consts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prints all the boards in a class."
    )
    parser.add_argument(
        "name", type=str, help="Filename without .json (e.g. make-eyes)"
    )
    args = parser.parse_args()

    rel_path = os.path.join(
        consts.TOP_LEVEL_PATH, "validation", "classes", f"{args.name}.json"
    )

    with open(rel_path, "r") as f:
        raw_json = f.read()

    all_boards = json.loads(raw_json)
    for b in all_boards["boards"]:
        print(board.boardFromBwBoardStr(b).ascii_board())
        print()
        print()
