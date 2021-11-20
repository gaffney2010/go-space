import json
import unittest
import unittest.mock

from go_space import board_lib
from go_space.go_types import player_lib, point_lib


class BoardTest(unittest.TestCase):
    @unittest.mock.patch("go_space.consts.SIZE", 3)
    def test_sgf_format(self):
        board = board_lib.Board()
        board.place(point_lib.Point.fromLabel("aa"), player_lib.Player.Black)
        board.place(point_lib.Point.fromLabel("ba"), player_lib.Player.White)
        board.place(point_lib.Point.fromLabel("ac"), player_lib.Player.Black)
        self.assertEqual(board.ascii_board(), ("#O.\n" "...\n" "#.."))

    @unittest.mock.patch("go_space.consts.SIZE", 3)
    def test_a1_format(self):
        board = board_lib.Board()
        board.place(point_lib.Point.fromLabel("A3"), player_lib.Player.Black)
        board.place(point_lib.Point.fromLabel("B3"), player_lib.Player.White)
        board.place(point_lib.Point.fromLabel("A1"), player_lib.Player.Black)
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
        board.place(point=point_lib.Point(row=1, col=1), player=player_lib.Player.White)
        board.place(point=point_lib.Point(row=0, col=1), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=2, col=1), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=1, col=0), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=1, col=2), player=player_lib.Player.Black)
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
        board.place(point=point_lib.Point(row=0, col=0), player=player_lib.Player.White)
        board.place(point=point_lib.Point(row=1, col=0), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=0, col=1), player=player_lib.Player.Black)
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
        board.place(point=point_lib.Point(row=1, col=1), player=player_lib.Player.White)
        board.place(point=point_lib.Point(row=1, col=2), player=player_lib.Player.White)
        board.place(point=point_lib.Point(row=2, col=2), player=player_lib.Player.White)
        board.place(point=point_lib.Point(row=0, col=1), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=0, col=2), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=0, col=3), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=1, col=0), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=1, col=3), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=2, col=1), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=2, col=3), player=player_lib.Player.Black)
        board.place(point=point_lib.Point(row=3, col=2), player=player_lib.Player.Black)
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
