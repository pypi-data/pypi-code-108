from __future__ import annotations

import math
from typing import List

from .position import Position


class Conductor:
    radius: float
    position: Position

    def __init__(self, radius: float, position: Position):
        self.radius = radius
        self.position = position

    @property
    def gmr(self) -> float:
        return self.radius*math.exp(-1/4)

    def distance(self, position: Position) -> float:
        x1, y1 = self.position.x, self.position.y
        x2, y2 = position.x, position.y
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def parse_conductors(conductors) -> List[Conductor]:
    conductors_list: List[Conductor] = []
    for conductor in conductors:
        if isinstance(conductor, Conductor):
            conductors_list.append(conductor)
        elif isinstance(conductor, dict):
            radius = conductor['radius']
            x, y = conductor['position']
            position = Position(x, y)
            conductors_list.append(Conductor(radius, position))
    return conductors_list
