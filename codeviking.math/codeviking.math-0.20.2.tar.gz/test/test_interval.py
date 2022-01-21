from codeviking.math.interval import RI


# TODO: separate tests by special cases (same as point_*_intersection


def test_RI():
    i = RI(-2, .83)
    assert -2.1 not in i
    assert -2.0 in i
    assert 0.8 in i
    assert 0.831 not in i


def test_RI_constrain():
    i = RI(-3.0, 1.0)
    assert i.constrain(0.8) == 0.8
    assert i.constrain(-33.0) == -3.0
    assert i.constrain(2.0) == 1.0


def test_RI_alpha():
    i = RI(-3.0, 1.0)
    assert i.alpha(-4.0) == -0.25
    assert i.alpha(3.0) == 1.5
    assert i.alpha(0.0) == 0.75


def test_RI_interpolate():
    i = RI(-3.0, 1.0)
    assert i.interpolate(0.0) == -3.0
    assert i.interpolate(0.5) == -1.0
    assert i.interpolate(1.0) == 1.0


def test_RI_is_empty():
    i0 = RI.empty
    assert i0.is_empty
    i1 = RI(10, -1)
    assert i1.is_empty


def test_RI_equal():
    i0 = (1, -1)
    assert RI.empty == i0
    i1 = RI(5, 10)
    i2 = RI(5, 10)
    assert i1 == i2
    assert i1 == (5, 10)


def test_RI_point_point_ne_intersection():
    i0 = RI(1.0, 1.0)
    i1 = RI(2.0, 2.0)
    i2 = RI(3.0, 3.0)
    assert i0.intersection(i1).is_empty
    assert i0.intersection(i2).is_empty
    assert i1.intersection(i2).is_empty


def test_RI_point_point_eq_intersection():
    i0 = RI(1.0, 1.0)
    i1 = RI(1.0, 1.0)
    i3 = i0.intersection(i1)
    assert i0.intersection(i1) == i0
    assert not i0.intersection(i1).is_empty


def test_RI_point_on_boundary_intersection():
    i0 = RI(1.0, 1.0)
    i1 = RI(2.0, 2.0)
    i2 = RI(1.0, 2.0)
    assert i0.intersection(i2) == RI(1.0, 1.0)
    assert i2.intersection(i0) == RI(1.0, 1.0)
    assert i1.intersection(i2) == RI(2.0, 2.0)
    assert i2.intersection(i1) == RI(2.0, 2.0)


def test_adjacent_interval_intersection():
    i0 = RI(1.0, 2.0)
    i1 = RI(2.0, 3.0)
    assert i0.intersection(i1) == RI(2.0, 2.0)
    assert i1.intersection(i0) == RI(2.0, 2.0)


def test_edge_inside_interval_intersection():
    i0 = RI(1.0, 1.2)
    i1 = RI(1.8, 2.0)
    i2 = RI(1.0, 2.0)
    assert i0.intersection(i2) == RI(1.0, 1.2)
    assert i2.intersection(i0) == RI(1.0, 1.2)

    assert i1.intersection(i2) == RI(1.8, 2.0)
    assert i2.intersection(i1) == RI(1.8, 2.0)


def test_intersection():
    i0 = RI(-1, 1)
    i1 = RI(0, 6)
    i2 = RI(5, 10)
    assert i0.intersection(i1) == RI(0, 1)
    assert i0.intersection(i2).is_empty
    assert i1.intersection(i2) == RI(5, 6)
    assert i0.intersection((-1, 0)) == (-1, 0)


def test_intersects():
    i0 = RI(-1, 1)
    i1 = RI(0, 6)
    i2 = RI(5, 10)
    assert i0.intersects(i1)
    assert not i0.intersects(i2)
    assert i1.intersects(i2)
    assert i0.intersects((-1, 0))
    assert not i0.intersects(RI.empty)
    assert not RI.empty.intersects(RI.empty)


def tests_expand():
    i0 = RI(-1, 1)
    i1 = RI(0, 6)
    i2 = RI(5, 10)
    assert i1.expand(i0) == i0.expand(i1)
    assert i0.expand(i1) == i1.expand(i0)
    assert i1.expand(i0) == RI(-1, 6)


def test_is_all():
    assert not RI.empty.is_all
    assert not RI(1.0, 1.0).is_all
    assert not RI(-2.0, 2.0).is_all
    assert RI(float('-inf'), float('inf')).is_all


def test_is_point():
    assert not RI.empty.is_point
    assert not RI(-10.4, 444.0).is_point
    assert RI(1.0, 1.0).is_point
    assert not RI(float('NaN'), float('NaN')).is_all
