import json
import unittest
import unittest.mock

from go_space import board_lib
from go_space.go_types import *


class BoardTest(unittest.TestCase):
    @unittest.mock.patch("go_space.consts.SIZE", 3)
    def test_sgf_format(self):
        board = board_lib.Board()
        board.place(Point.fromLabel("aa"), Player.Black)
        board.place(Point.fromLabel("ba"), Player.White)
        board.place(Point.fromLabel("ac"), Player.Black)
        self.assertEqual(board.ascii_board(), ("#O.\n" "...\n" "#.."))

    @unittest.mock.patch("go_space.consts.SIZE", 3)
    def test_a1_format(self):
        board = board_lib.Board()
        board.place(Point.fromLabel("A3"), Player.Black)
        board.place(Point.fromLabel("B3"), Player.White)
        board.place(Point.fromLabel("A1"), Player.Black)
        self.assertEqual(board.ascii_board(), ("#O.\n" "...\n" "#.."))

    @unittest.mock.patch("go_space.consts.SIZE", 3)
    def test_json_read(self):
        json_str = '{"black": ["aa", "ac"], "white": ["ba"]}'
        brd = json.loads(json_str)
        self.assertEqual(
            board_lib.boardFromBwBoardStr(brd).ascii_board(), ("#O.\n" "...\n" "#..")
        )

    def test_remove_stones(self):
        board = board_lib.Board()
        board.place(point=Point(row=1, col=1), player=Player.White)
        board.place(point=Point(row=0, col=1), player=Player.Black)
        board.place(point=Point(row=2, col=1), player=Player.Black)
        board.place(point=Point(row=1, col=0), player=Player.Black)
        board.place(point=Point(row=1, col=2), player=Player.Black)
        self.assertEqual(
            board.ascii_board(),
            """.#.................
               #.#................
               .#.................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................""".replace(
                " ", ""
            ),
        )

    def test_remove_stones_corner(self):
        board = board_lib.Board()
        board.place(point=Point(row=0, col=0), player=Player.White)
        board.place(point=Point(row=1, col=0), player=Player.Black)
        board.place(point=Point(row=0, col=1), player=Player.Black)
        self.assertEqual(
            board.ascii_board(),
            """.#.................
               #..................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................""".replace(
                " ", ""
            ),
        )

    def test_remove_stones_blob(self):
        board = board_lib.Board()
        board.place(point=Point(row=1, col=1), player=Player.White)
        board.place(point=Point(row=1, col=2), player=Player.White)
        board.place(point=Point(row=2, col=2), player=Player.White)
        board.place(point=Point(row=0, col=1), player=Player.Black)
        board.place(point=Point(row=0, col=2), player=Player.Black)
        board.place(point=Point(row=0, col=3), player=Player.Black)
        board.place(point=Point(row=1, col=0), player=Player.Black)
        board.place(point=Point(row=1, col=3), player=Player.Black)
        board.place(point=Point(row=2, col=1), player=Player.Black)
        board.place(point=Point(row=2, col=3), player=Player.Black)
        board.place(point=Point(row=3, col=2), player=Player.Black)
        self.assertEqual(
            board.ascii_board(),
            """.###...............
               #..#...............
               .#.#...............
               ..#................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................
               ...................""".replace(
                " ", ""
            ),
        )
