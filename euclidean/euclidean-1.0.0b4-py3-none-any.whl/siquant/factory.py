from siquant import Quantity

import euclidean.siquant.vector as v

from euclidean.R2.cartesian import V2
from euclidean.R3.cartesian import V3
from euclidean.util import methods


def make_factory(*quantity_types):
    def factory(q, u):
        for q_type in quantity_types:
            if isinstance(q, q_type._TYPE):
                return q_type(q, u)
        return Quantity(q, u)

    return staticmethod(factory)


@methods(
    v.angle,
    v.unit,
    v.rotate,
    v.magnitude,
    v.approx,
    v.cross,
    v.dot,
    v.is_parallel,
    v.is_orthogonal,
    v.manhattan_distance,
)
class V2Quantity(Quantity):
    __slots__ = ()
    _TYPE = V2

    x = property(lambda self: self.quantity.x * self.units)
    y = property(lambda self: self.quantity.y * self.units)


@methods(
    v.angle,
    v.unit,
    v.magnitude,
    v.approx,
    v.cross,
    v.dot,
    v.is_parallel,
    v.is_orthogonal,
    v.manhattan_distance,
)
class V3Quantity(Quantity):
    __slots__ = ()

    _TYPE = V3

    x = property(lambda self: self.quantity.x * self.units)
    y = property(lambda self: self.quantity.y * self.units)
    z = property(lambda self: self.quantity.z * self.units)

    def xy(self):
        return self.quantity.xy() * self.units

    def xz(self):
        return self.quantity.xz() * self.units

    def yz(self):
        return self.quantity.yz() * self.units
