import unittest
import unittest.mock

from board import *


class BoardTest(unittest.TestCase):
    @unittest.mock.patch("consts.SIZE", 3)
    def test_sgf_format(self):
        board = Board()
        board.place(Point.fromLabel("aa"), Player.Black)
        board.place(Point.fromLabel("ba"), Player.White)
        board.place(Point.fromLabel("ac"), Player.Black)
        self.assertEqual(board.ascii_board(), ("#O.\n" "...\n" "#.."))

    @unittest.mock.patch("consts.SIZE", 3)
    def test_a1_format(self):
        board = Board()
        board.place(Point.fromLabel("A3"), Player.Black)
        board.place(Point.fromLabel("B3"), Player.White)
        board.place(Point.fromLabel("A1"), Player.Black)
        self.assertEqual(board.ascii_board(), ("#O.\n" "...\n" "#.."))

    @unittest.mock.patch("consts.SIZE", 3)
    def test_json_read(self):
        json = '{"blacks": ["aa", "ac"], "whites": ["ba"]}'
        self.assertEqual(
            boardFromJson(json).ascii_board(), ("#O.\n" "...\n" "#..")
        )
