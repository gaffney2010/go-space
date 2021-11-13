import attr

from go_space.types import player, point


@attr.s(frozen=True)
class Stone(object):
    point: point.Point = attr.ib()
    player: player.Player = attr.ib()
