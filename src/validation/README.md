This folder contains the source of truth that we'll score against.

An embedding space scores higher if it:
1. Puts points of the same class close, and
2. Puts points of different classes far apart.

To achieve this, embedding spaces are scored using Buhlmann credibility.

Each file in this folder contains a class of boards, representing mutually
similar board positions.  This is stored as a json with a top-level `boards`
variable.  Each board then has top-level `blacks` and `whites` variables, which
are lists of strings spots on the boards.  (See board_test.py for examples.)
