import attr

from . import player_lib, point_lib


@attr.s(frozen=True)
class Stone(object):
    point: point_lib.Point = attr.ib()
    player: player_lib.Player = attr.ib()
