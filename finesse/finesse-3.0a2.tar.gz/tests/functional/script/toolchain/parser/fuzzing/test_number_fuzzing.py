"""Kat file parser number parsing fuzzing tests."""

import numpy as np
from hypothesis import given, assume, settings
from hypothesis.strategies import integers, floats, complex_numbers


_INT_DTYPE_INFO = np.iinfo(np.int32)
MIN_INT = _INT_DTYPE_INFO.min
MAX_INT = _INT_DTYPE_INFO.max


# Need bounds on integers due to Numpy. See #119.
@given(value=integers(min_value=MIN_INT, max_value=MAX_INT))
@settings(deadline=1000)  # See #292.
def test_integer_fuzzing(fuzz_value_parse_compare, value):
    fuzz_value_parse_compare(value, value)


@given(value=floats(allow_nan=False, allow_infinity=True))
@settings(deadline=1000)  # See #292.
def test_float_fuzzing(fuzz_value_parse_compare, value):
    assume(not str(value).endswith("e"))
    fuzz_value_parse_compare(value, value)


@given(value=complex_numbers(allow_nan=False, allow_infinity=False))
@settings(deadline=1000)  # See #292.
def test_complex_fuzzing(fuzz_value_parse_compare, value):
    fuzz_value_parse_compare(value, value)
