"""Symbol fuzzing tests."""

import math
import cmath
from hypothesis import given
from hypothesis.strategies import floats, complex_numbers
from finesse.symbols import FUNCTIONS


@given(number=floats(allow_infinity=False, allow_nan=False))
def test_expression_fuzzing_with_floats(number):
    """Test that expressions with numbers evaluate to the correct values."""
    assert math.isclose(FUNCTIONS["cos"](number).eval(), math.cos(number))


# Maximum magnitude is set to avoid math range errors and infinities.
@given(number=complex_numbers(max_magnitude=1e2))
def test_expression_fuzzing_with_complex_numbers(number):
    """Test that expressions with numbers evaluate to the correct values."""
    assert cmath.isclose(FUNCTIONS["exp"](number).eval(), cmath.exp(number))
