import enum

import attr


class FormatError(Exception):
    pass


class PointFormatError(FormatError):
    pass


@attr.s(frozen=True)
class Point(object):
    # By convention start counting from top-left
    row: int = attr.ib()  # Zero-indexed
    col: int = attr.ib()  # Zero-indexed

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
        raise PointFormatError("This should never happen")


class Player(enum.Enum):
    Black = 1
    White = 2
    # Special "Players" for debugging
    Spec1 = 3
    Spec2 = 4


@attr.s(frozen=True)
class Stone(object):
    point: Point = attr.ib()
    player: Player = attr.ib()