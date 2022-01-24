from baby_steps import given, then, when
from district42 import schema

from .._fixtures import *  # noqa: F401, F403


def test_const_generation(*, generate, random_):
    with given:
        sch = schema.const

    with when:
        res = generate(sch)

    with then:
        assert res is None


def test_const_value_generation(*, generate, random_):
    with given:
        val = "banana"
        sch = schema.const(val)

    with when:
        res = generate(sch)

    with then:
        assert res == val
