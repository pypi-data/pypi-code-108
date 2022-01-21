import math

from codeviking.math.geom2d import V2, Tri2, Box2, ConvPoly2
from codeviking.math.interval import RI
from codeviking.math.comparisons import make_equals

eq = make_equals(1e-8, 1e-8)


def test_length():
    u = V2(3, 4)
    assert (u.length == 5.0)


def test_equals():
    u = V2(3, 4)
    v = V2(3, 4)
    w = (3, 4)
    assert (u == v)
    assert (u == w)


def test_dot_product():
    u = V2(2, -3)
    v = V2(1, 7)
    assert (u @ v == 2 * 1 - 3 * 7)
    assert (u.dot(v) == 2 * 1 - 3 * 7)
    assert (v @ u == 2 * 1 - 3 * 7)
    assert (v.dot(u) == 2 * 1 - 3 * 7)


def test_dot_product_tuple():
    u = V2(2, -3)
    v = (1, 7)
    assert (u @ v == 2 * 1 - 3 * 7)
    assert (u.dot(v) == 2 * 1 - 3 * 7)


def test_sub():
    u = V2(2, -3)
    v = V2(1, 7)
    assert (u - v == V2(1, -10))


def test_sub_tuple():
    u = V2(2, -3)
    v = (1, 7)
    assert (u - v == (1, -10))


def test_scalar_mult():
    u = V2(2, -3)
    assert (u * 2 == V2(4, -6))
    assert (2 * u == V2(4, -6))


def test_scalar_div():
    u = V2(2, -3)
    assert (u / 2.0 == V2(1, -1.5))


def test_scalar_floordiv():
    u = V2(9, -3)
    assert (u // 2 == V2(4, -2))


def test_neg():
    u = V2(2, -3)
    assert -u == V2(-2, 3)


def test_project_onto_x():
    u = V2(2, -3)
    p = u.project_onto(V2(1, 0))
    assert eq(p.x, 2.0) and eq(p.y, 0.0)


def test_project_onto_y():
    u = V2(2, -3)
    p = u.project_onto(V2(0, 1))
    assert eq(p.x, 0.0) and eq(p.y, -3.0)


def test_project_onto():
    u = V2(2, 3)
    p = u.project_onto(V2(2, 1))
    assert eq(p.x, 2.8) and eq(p.y, 1.4)


def test_tri():
    t = Tri2((0, 0), (1, 0), (0, 1))
    assert ((0.5, 0.8) not in t)
    assert ((0.8, 0.1) in t)
    assert ((0.5, 0.5) in t)
    assert ((1, 0) in t)
    assert ((0, 0) in t)
    assert ((0, 1) in t)
    assert ((1, 1) not in t)


def test_poly():
    q = ConvPoly2([(0, 0), (1, 0), (1, 2), (0, 1)])
    assert ((0.5, 0.8) in q)
    assert ((1.8, 0.1) not in q)
    assert ((1.5, 0.5) not in q)
    assert ((0, 0) in q)
    assert ((1, 0) in q)
    assert ((1, 2) in q)
    assert ((0, 1) in q)


def test_box2_expand():
    b = Box2((0, 1), (2, 3))
    assert b.expand((0.5, 2.4)) == b
    assert b.expand(Box2((0, 2), (-2, 1))) == Box2((0, 2), (-2, 3))


def test_box2_empty_expand():
    b = Box2.empty.expand((0, 0))
    assert b.expand((1, 1)) == Box2((0, 1), (0, 1))


def test_box2_is_empty():
    b = Box2((0, 1), (2, 3))
    assert not b.is_empty
    assert Box2((1, -1), (1, -1)).is_empty
    assert Box2((1, -1), (1, 2)).is_empty
    assert Box2((1, 2), (1, -1)).is_empty
    assert Box2.empty.is_empty


def test_ri_expand():
    i = RI(0, 1)
    assert i.expand((0.5, 2.4)) == RI(0, 2.4)
    assert i.expand(5) == RI(0, 5)
    assert i.expand(0.1) == i


def test_ri_empty_expand():
    i = RI.empty
    assert i.expand((0, 1)) == RI(0, 1)
    assert i.expand(1) == RI(1, 1)


def test_ri_is_empty():
    i = RI(0, 1)
    assert not i.is_empty
    assert RI.empty.is_empty


def test_ri_intersects():
    a = RI(10, float('inf'))
    b = RI(float('-inf'), 20)
    c = RI(-1, 2)
    d = RI(0, 1)
    e = RI(4, 8)

    assert a.intersects(b)
    assert not a.intersects(c)
    assert not a.intersects(d)
    assert not a.intersects(e)
    assert b.intersects(c)
    assert b.intersects(d)
    assert b.intersects(e)
    assert c.intersects(d)
    assert not c.intersects(e)
    assert not d.intersects(e)


def test_ri_intersection():
    a = RI(10, float('inf'))
    b = RI(float('-inf'), 20)
    c = RI(-1, 2)
    d = RI(0, 1)
    e = RI(4, 8)

    assert a.intersection(b) == (10, 20)
    assert a.intersection(c).is_empty
    assert a.intersection(d).is_empty
    assert a.intersection(e).is_empty
    assert b.intersection(c) == c
    assert b.intersection(d) == d
    assert b.intersection(e) == e
    assert c.intersection(d) == (0, 1)
    assert c.intersection(e).is_empty
    assert d.intersection(e).is_empty


def test_box_intersects():
    a = Box2((1, 4), (-1, 3))
    b = Box2((-13, -2), (0, 2))
    c = Box2((0, 10), (0, 10))
    d = Box2((0, 5), (-2, 4))

    assert not a.intersects(b)
    assert a.intersects(c)
    assert a.intersects(d)


def test_box_intersection():
    a = Box2((1, 4), (-1, 3))
    b = Box2((-13, 20), (0, 2))
    c = Box2((0, 10), (0, 10))
    d = Box2((0, 5), (-2, 4))

    assert a.intersection(b) == Box2((1, 4), (0, 2))
    assert a.intersection(c) == Box2((1, 4), (0, 3))
    assert a.intersection(d) == Box2((1, 4), (-1, 3))


def test_angle_45():
    eq = make_equals(1E-14, 1E-7)
    sqrt2 = math.sqrt(2.0)
    v = V2(sqrt2, sqrt2)
    assert eq(v.angle, math.pi / 4)
    assert eq(v.angle_deg, 45)

    u = v.unit
    assert eq(u.x, math.cos(math.pi / 4))
    assert eq(u.y, math.sin(math.pi / 4))

    t = V2.from_angle(math.pi / 4)
    s = V2.from_angle_deg(45)

    assert eq(u.x, t.x)
    assert eq(u.y, t.y)

    assert eq(u.x, s.x)
    assert eq(u.y, s.y)


def test_angle_n60():
    eq = make_equals(1E-14, 1E-7)
    sqrt3 = math.sqrt(3.0)
    v = V2(1, -sqrt3)
    assert eq(v.angle, 5 * math.pi / 3)
    assert eq(v.angle_deg, 300.0)

    u = v.unit
    assert eq(u.x, 0.5)
    assert eq(u.y, -sqrt3 / 2.0)

    t = V2.from_angle(-math.pi / 3)
    s = V2.from_angle_deg(-60)

    assert eq(u.x, t.x)
    assert eq(u.y, t.y)

    assert eq(u.x, s.x)
    assert eq(u.y, s.y)
