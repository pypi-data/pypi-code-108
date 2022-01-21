from codeviking.math.geom2d import Segment2, V2
from codeviking.math.comparisons import make_equals

eq = make_equals(1e-7, 1e-7)


def point_eq(a, b):
    delta = b - a
    return eq(delta.length, 0.0)


def test_segment_orth():
    s1 = Segment2(V2(1.0, 1.0), V2(2.0, 2.0))
    s2 = Segment2(V2(1.0, 2.0), V2(2.0, 1.0))
    ii = s1.intersect(s2)
    delta = ii - V2(1.5, 1.5)
    assert eq(delta.length, 0.0)


def test_segment_orth_endpoint():
    s1 = Segment2(V2(1.0, 1.0), V2(2.0, 2.0))
    s2 = Segment2(V2(1.5, 1.5), V2(2.0, 1.0))
    ii = s1.intersect(s2)
    delta = ii - V2(1.5, 1.5)
    assert eq(delta.length, 0.0)


def test_segment_orth_near_endpoint():
    s1 = Segment2(V2(1.0, 1.0), V2(2.0, 2.0))
    s2 = Segment2(V2(1.52, 1.51), V2(2.0, 1.0))
    ii = s1.intersect(s2)
    assert ii is None


def test_segment_parallel_inter():
    s1 = Segment2(V2(1.0, 1.0), V2(2.0, 2.0))
    s2 = Segment2(V2(1.01, 1.01), V2(2.01, 2.01))
    ii = s1.intersect(s2)
    pa = V2(1.01, 1.01)
    pb = V2(2.0, 2.0)
    assert point_eq(ii.a, pa)
    assert point_eq(ii.b, pb)


def test_segment_parallel_no_inter():
    s1 = Segment2(V2(1.0, 1.0), V2(2.0, 2.0))
    s2 = Segment2(V2(1.01, 1.00), V2(2.01, 2.00))
    ii = s1.intersect(s2)
    assert ii is None


def test_segment_near_parallel_point():
    s1 = Segment2(V2(1.0, -1.0000001), V2(-1.0, -0.9999999))
    s2 = Segment2(V2(1.0, -0.9999999), V2(-1.0, -1.0000001))
    ii = s1.intersect(s2)
    assert point_eq(ii, V2(0.0, -1.0))


def test_segment_rev1_inter():
    ra = V2(-1, 0)
    rb = V2(1, 1)
    sa = V2(1, 2)
    sb = V2(-2, -2)
    r = Segment2(ra, rb)
    s = Segment2(sa, sb)
    rsi = V2(-0.2, 0.4)
    assert point_eq(r.intersect(s), rsi)


def test_segment_rev2_inter():
    pa = V2(0, 1)
    pb = V2(1, 0)
    qa = V2(0, 0)
    qb = V2(1, 1)
    p = Segment2(pa, pb)
    q = Segment2(qa, qb)
    pqi = V2(0.5, 0.5)
    assert point_eq(p.intersect(q), pqi)


def test_side_on():
    s = Segment2(V2(1, 1.5), V2(0, 1.0))
    assert eq(s.side(V2(0.5, 1.25)), 0)


def test_side_left():
    s = Segment2(V2(1, 1.5), V2(0, 1.0))
    assert s.side(V2(5, -10)) < 0


def test_side_right():
    s = Segment2(V2(1, 1.5), V2(0, 1.0))
    assert s.side(V2(0, 10.)) > 0
