import numpy as np

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x + other, self.y + other)
        else:
            return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x - other, self.y - other)
        else:
            return Point(self.x - other.x, self.y - other.y)

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    @staticmethod
    def zero():
        return Point(0., 0.)

    @staticmethod
    def distance(vec1, vec2) -> float:
        return np.sqrt(np.square(vec1.x - vec2.x) + np.square(vec1.y - vec2.y))

    @staticmethod
    def limited(value: float, range) -> bool:
        if range.x <= value <= range.y:
            return True
        else:
            return False
