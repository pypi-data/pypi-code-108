import pytest


def test_remove_mirror(model):
    model.parse("mirror m1")
    assert "m1" in model.elements
    model.remove(model.m1)
    assert "m1" not in model.elements


def test_remove_space(model):
    model.parse("mirror m1")
    model.parse("mirror m2")
    model.parse("space s1 portA=m1.p2 portB=m2.p1")
    assert "s1" in model.elements
    model.remove(model.elements["s1"])
    assert "s1" not in model.elements


def test_string(model):
    model.parse("mirror m1")
    assert "m1" in model.elements
    model.remove("m1")
    assert "m1" not in model.elements


def test_error_on_unrecognised(model):
    with pytest.raises(TypeError, match=r".*not recongised.*"):
        model.remove(10)
