#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

from collections import abc

import pytest

from pyxel.models.photon_generation import illumination
from pyxel.pipelines import Arguments, ModelFunction


@pytest.fixture
def model_function() -> ModelFunction:
    """Create a valid `ModelFunction` instance."""
    return ModelFunction(
        name="illumination",
        func=illumination,
        arguments={"level": 1, "option": "foo"},
    )


def test_type_model_function(model_function: ModelFunction):
    assert isinstance(model_function, ModelFunction)
    assert callable(model_function)


@pytest.mark.skip(reason="Class `Arguments` is not implemented")
def test_type_arguments(model_function: ModelFunction):
    assert isinstance(model_function.arguments, Arguments)
    assert isinstance(model_function.arguments, abc.Mapping)


@pytest.mark.parametrize("key", ["level", "option"])
def test_arguments_contain(model_function, key):
    assert isinstance(model_function, ModelFunction)
    assert key in model_function.arguments


@pytest.mark.parametrize("key", ["", "LEVEL", "foo"])
def test_arguments_not_contains(model_function, key):
    assert isinstance(model_function, ModelFunction)
    assert key not in model_function.arguments


@pytest.mark.parametrize("key, exp_value", [("level", 1), ("option", "foo")])
def test_arguments_getitem(model_function, key, exp_value):
    assert model_function.arguments[key] == exp_value


def test_arguments_iter(model_function):
    assert list(model_function.arguments) == ["level", "option"]


def test_arguments_len(model_function):
    assert len(model_function.arguments) == 2


@pytest.mark.skip(reason="Class `Arguments` is not implemented")
def test_arguments_getattr(model_function):
    assert model_function.arguments.level == 1


def test_arguments_getattr_error(model_function):
    with pytest.raises(AttributeError):
        _ = model_function.arguments.Level


@pytest.mark.skip(reason="Class `Arguments` is not implemented")
def test_get_level(model_function):
    assert isinstance(model_function, ModelFunction)

    result = model_function.arguments.level
    assert result == 1
