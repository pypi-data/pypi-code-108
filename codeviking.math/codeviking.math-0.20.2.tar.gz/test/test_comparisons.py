from codeviking.math.comparisons import *


def test_make_equals():
    eq0 = make_equals(0.1, 0.5)
    assert eq0(1, 2)
    assert not eq0(1, 2.1)
    assert eq0(1, 1.1)

    assert eq0(10, 20)
    assert eq0(10, 11)

    assert not eq0(10, 20.1)
    assert not eq0(10, 20.1)


def test_make_relative_equals():
    eq0 = make_relative_equals(0.1)
    assert eq0(1.0, 1.1)
    assert not eq0(1.0, 1.2)


def test_make_seq_equals():
    eq0 = make_seq_equals(make_relative_equals(0.1))
    s0 = (1.0, 2.0, 3.0, 4.0)
    s1 = (1.1, 2.2, 3.3, 4.4)
    s2 = (1.0, 2.0, 3.4, 4.5)
    s3 = (1.0, 2.0, 3.0)
    assert eq0(s0, s1)
    assert eq0(s1, s2)
    assert not eq0(s0, s2)
    assert not eq0(s0, s3)
