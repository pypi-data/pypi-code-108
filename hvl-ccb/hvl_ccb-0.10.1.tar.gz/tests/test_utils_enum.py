#  Copyright (c) 2019-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for Enum utils.
"""

import pytest

from hvl_ccb.utils.enum import (
    AutoNumberNameEnum,
    NameEnum,
    StrEnumBase,
    ValueEnum,
    RangeEnum,
    unique,
    BoolEnum,
)


def test_strenumbase():
    @unique
    class E(StrEnumBase):
        A = "a"

    with pytest.raises(NotImplementedError):
        E.A == "a"


def test_valueenum():

    with pytest.raises(ValueError):
        @unique
        class F(ValueEnum):
            A = "a"
            B = "a"

    @unique
    class E(ValueEnum):
        A = "a"
        B = "b"

    a = E("a")
    assert hash(a) == hash(a.value)
    assert a.value == a
    assert a == "a"
    assert str(a) == "a"
    assert a == E.A

    assert E["A"] is a
    with pytest.raises(KeyError):
        E["a"]
    with pytest.raises(KeyError):
        E[a]

    assert a != 0
    assert a != 1

    b = E("b")
    assert hash(b) == hash(b.value)
    assert a != b
    assert a != "b"
    assert a != E.B


def test_nameenum():

    class E(NameEnum):
        _init_ = 'custom_name'
        a = 2
        b = 4

    a = E("a")
    assert hash(a) == hash(a.name)
    assert a.name == a
    assert a == "a"
    assert str(a) == "a"
    assert a == E.a

    assert a != 2
    assert a.custom_name == 2

    assert E["a"] is a
    assert E[a] is a

    b = E("b")
    assert hash(b) == hash(b.name)
    assert a != b
    assert a != "b"
    assert a != E.b


def test_autonumbernameenum():

    class E(AutoNumberNameEnum):
        a = ()
        b = ()

    a = E("a")
    assert hash(a) == hash(a.name)
    assert a.name == a
    assert a == "a"
    assert str(a) == "a"
    assert a == E.a

    assert a != 0
    assert a != 1

    assert E["a"] is a
    assert E[a] is a

    b = E("b")
    assert hash(b) == hash(b.name)
    assert a != b
    assert a != "b"
    assert a != E.b


def test_rangeenum():

    class E(RangeEnum):
        TWO = 2
        ONE = 1

        @classmethod
        def unit(cls):
            return "V"

    assert E(1) == 1
    assert E(1.5) == 2
    assert E(0.1) == 1

    assert E.TWO == 2
    assert E(1.5) == E.TWO
    assert str(E.ONE) == "1.0"

    assert E.unit() == "V"

    with pytest.raises(TypeError):
        E("a")
    with pytest.raises(ValueError):
        E(5)

    assert hash(E(1)) == hash(E.ONE)
    assert E.ONE != E.TWO
    assert E.ONE != "1"
    assert E.ONE != 2


def test_boolenum():
    class SingleTruth(BoolEnum):
        TRUE = True
        FALSE = False

    assert SingleTruth.TRUE
    assert not SingleTruth.FALSE
    assert bool(SingleTruth.TRUE)
    assert not bool(SingleTruth.FALSE)

    assert SingleTruth.TRUE.name == "TRUE"
    assert SingleTruth.TRUE.value
    assert not SingleTruth.FALSE.value

    class InvertedTruth(BoolEnum, init="truth inverted"):
        TRUE = True, "False"
        FALSE = False, "True"

    assert InvertedTruth.TRUE
    assert not InvertedTruth.FALSE
    assert InvertedTruth.TRUE.inverted == "False"
    assert InvertedTruth.FALSE.inverted == "True"

    assert InvertedTruth.TRUE.value == (True, "False")

    with pytest.raises(TypeError):
        class WrongClass(BoolEnum):
            MEMBER = "str"

    with pytest.raises(ValueError):
        class WrongInitNameClass(BoolEnum, init="value invert"):
            MEMBER = True, "str"
