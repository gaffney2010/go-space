from typing import Iterator, Tuple

import attr

from go_space import consts, exceptions


@attr.s(frozen=True)
class Point(object):
    # By convention start counting from top-left
    row: int = attr.ib()  # Zero-indexed
    col: int = attr.ib()  # Zero-indexed

    # TODO: Change name of to/from_dict everywhere.
    # Despite being called `to_dict`, we prefer a tuple cast, since the object is immutable.
    def to_dict(self) -> Tuple[int]:
        """Should contain all the info needed to reconstruct."""
        return (self.row, self.col)

    @staticmethod
    def from_dict(data: Tuple[int]) -> "Point":
        """Rebuild from one of the to_dict saved dicts."""
        return Point(row=data[0], col=data[1])

    def mod_row_col(self) -> Tuple[int, int]:
        """Gives coordinates after rotating to get point in low-index quarter."""
        half_board = consts.SIZE // 2 + 1
        r, c = self.row, self.col

        if r >= half_board:
            r = consts.SIZE - 1 - r
        if c >= half_board:
            c = consts.SIZE - 1 - c

        return r, c

    @classmethod
    def fromLabel(cls, label: str) -> "Point":
        """Returns a Point from a label

        Arguments:
            label: May be in the format "A1" where "A" is the left-most column
                and "1" is the bottom-most row.  Or in the SGF format "aa" where
                the first letter is the left-most column, and the second letter
                is the top-most row.

        Returns:
            A Point class with the specified label.
        """
        first, second = label[0], label[1:]
        try:
            format = "A1"
            number = int(second)
        except:
            format = "SGF"

        if format == "A1":
            letter = first.upper()
            col = ord(letter) - ord("A")
            # Start from bottom with number=1 maps to consts.SIZE-1
            row = consts.SIZE - number
            return Point(row=row, col=col)
        if format == "SGF":
            first = first.lower()
            second = second.lower()
            col = ord(first) - ord("a")
            row = ord(second) - ord("a")
            return Point(row=row, col=col)
        raise exceptions.PointFormatError("This should never happen")
