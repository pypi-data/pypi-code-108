"""Test cases for selecting modes to include in a model."""

from finesse import Model
from hypothesis import given, assume
from hypothesis.strategies import one_of, composite, integers, complex_numbers, floats
import pytest


@pytest.fixture(scope="module")
def model():
    """Fixture with module scope for quick fuzzing tests."""
    return Model()


@composite
def non_whole_floats(draw):
    value = draw(floats())
    if value.is_integer():
        assume(False)
    return value


@given(maxtem=integers(max_value=-1))
def test_negative_integer_maxtem_is_invalid(model, maxtem):
    """Test that maxtem cannot be negative integer."""
    with pytest.raises(ValueError):
        model.modes(maxtem=maxtem)


@given(maxtem=one_of(non_whole_floats(), complex_numbers()))
def test_non_integer_maxtem_is_invalid(model, maxtem):
    """Test that maxtem cannot be non-integer."""
    with pytest.raises((ValueError, TypeError)):
        model.modes(maxtem=maxtem)
