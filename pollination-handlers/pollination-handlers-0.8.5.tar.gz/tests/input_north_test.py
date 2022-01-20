from pollination_handlers.inputs.north import north_vector_to_angle

from ladybug_geometry.geometry2d.pointvector import Vector2D
import pytest


def test_north_vector_to_angle():
    res = north_vector_to_angle(20)
    assert res == 20
    res = north_vector_to_angle('20')
    assert res == 20
    res = north_vector_to_angle(Vector2D(1, 0))
    assert res == pytest.approx(270, rel=1e-3)
    res = north_vector_to_angle(Vector2D(-1, 0))
    assert res == pytest.approx(90, rel=1e-3)
