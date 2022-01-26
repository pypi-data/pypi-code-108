import math
from functools import reduce
from typing import List


class Position:
    x: float
    y: float

    def __init__(self, x: float, y: float, polar: bool = False):
        if polar:
            self.x = x * math.cos(y)
            self.y = x * math.sin(y)
        else:
            self.x = x
            self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Position({self.x}, {self.y})"

    def __getitem__(self, item: int) -> float:
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError("Index out of range")


def geometric_mean_position(positions: List[Position]) -> Position:
    x_list = [position.x for position in positions]
    y_list = [position.y for position in positions]
    x = reduce(lambda a, b: a*b, x_list)**(1/len(x_list))
    y = reduce(lambda a, b: a*b, y_list)**(1/len(y_list))
    return Position(x, y)
