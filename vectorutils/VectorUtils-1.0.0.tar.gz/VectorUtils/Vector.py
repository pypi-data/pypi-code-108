

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
