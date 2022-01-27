#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#

import pytest

from pyxel.pipelines import Arguments


@pytest.fixture
def arguments() -> Arguments:
    """Create a valid `Arguments` instance."""
    args = {"one": 1, "two": 2, "three": 3}
    return Arguments(args)


def test_type_model_function(arguments: Arguments):
    assert isinstance(arguments, Arguments)


def test_getitem(arguments: Arguments):
    assert arguments["one"] == 1


def test_getitem_key_error(arguments: Arguments):
    with pytest.raises(KeyError):
        _ = arguments["four"]


def test_setitem(arguments: Arguments):
    arguments["two"] = 0
    assert arguments["two"] == 0


def test_setitem_key_error(arguments: Arguments):
    with pytest.raises(KeyError):
        arguments["four"] = 4


def test_getattr(arguments: Arguments):
    assert arguments.one == 1
    assert arguments._arguments == {"one": 1, "two": 2, "three": 3}


def test_getattr_attribute_error(arguments: Arguments):
    with pytest.raises(AttributeError):
        _ = arguments.four


def test_setattr(arguments: Arguments):
    arguments.two = 0
    assert arguments.two == 0


def test_setattr_attribute_error(arguments: Arguments):
    with pytest.raises(AttributeError):
        arguments.four = 4


def test_len(arguments: Arguments):
    assert len(arguments) == 3
