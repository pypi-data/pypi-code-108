from math import sqrt, atan2, hypot


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getMag(self):
        return sqrt(self.x**2 + self.y**2)

    def setMag(self, magnitude):
        newX = self.x * magnitude / self.getMag()
        newY = self.y * magnitude / self.getMag()
        self.x = newX
        self.y = newY

    def getAngle(self, other):
        return atan2((other.y - self.y), (other.x - self.x))

    def getDist(self, other):
        return hypot((other.x - self.x), (other.y - self.y))

    def toTuple(self):
        return self.x, self.y

    def toInt(self):
        return Vector2(int(self.x), int(self.y))

    def toFloat(self):
        return Vector2(float(self.x), float(self.y))

    def __add__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x + other.x, self.y + other.y)
        elif type(other) == int or float:
            return Vector2(self.x + other, self.y + other)

    def __sub__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x - other.x, self.y - other.y)
        elif type(other) == int or float:
            return Vector2(self.x - other, self.y - other)

    def __mul__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x * other.x, self.y * other.y)
        elif type(other) == int or float:
            return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x / other.x, self.y / other.y)
        elif type(other) == int or float:
            return Vector2(self.x / other, self.y / other)
