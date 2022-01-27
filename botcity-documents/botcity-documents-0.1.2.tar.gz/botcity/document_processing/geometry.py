from __future__ import annotations
from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from typing import Union, List


@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Polygon:
    points: List[Point]

    @property
    def rect(self):
        p1, _, p3, _ = self.points
        return p1.x, p1.y, p3.x, p3.y

    def contains(self, other: Union[Polygon, Point])->bool:
        x0, y0, x1, y1 = self.rect
        if isinstance(other, Polygon):
            ox0, oy0, ox1, oy1 = other.rect
            return x0 <= ox0 <= ox1 <= x1 and y0 <= oy0 <= oy1 <= y1
        elif isinstance(other, Point):
            # (x > x1 and x < x2 and y > y1 and y < y2)
            ox, oy = other.x, other.y
            return x0 <= ox <= x1 and y0 <= oy <= y1
        else:
            raise ValueError("Invalid type for contains. Only Polygon and Point accepted.")
