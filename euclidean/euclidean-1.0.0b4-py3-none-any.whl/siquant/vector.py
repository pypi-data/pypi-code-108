from siquant import make, si


def rotate(self, angle):
    return make(self.quantity.rotate(angle.get_as(si.radians)), self.units)


def unit(self):
    return make(self.quantity.unit(), si.unity)


def dot(self, other):
    return make(self.quantity.dot(other.quantity), self.units * other.units)


def cross(self, other):
    return make(self.quantity.cross(other.quantity), self.units * other.units)


def magnitude(self):
    return make(self.quantity.magnitude(), self.units)


def angle(self, other):
    if not hasattr(other, "quantity"):
        return make(self.quantity.angle(other), si.radians)
    return make(self.quantity.angle(other.quantity), si.radians)


def approx(self, other):
    return self.quantity.approx(other.quantity)


def is_parallel(self, other):
    if not hasattr(other, "quantity"):
        return self.quantity.is_parallel(other)
    return self.quantity.is_parallel(other.quantity)


def is_orthogonal(self, other):
    if not hasattr(other, "quantity"):
        return self.quantity.is_orthogonal(other)
    return self.quantity.is_orthogonal(other.quantity)


def manhattan_distance(self):
    return make(self.quantity.manhattan_distance(), self.units)
