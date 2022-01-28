"""Some fast C level functions implemented in finesse.cymath use explicitly hard-coded
values or look-up tables.

These are tested against general implementations (from scipy) here.
"""

import numpy as np
from numpy.testing import assert_allclose
import pytest

import scipy.special as scs
import finesse.cymath as cymath


@pytest.mark.parametrize("x", (np.pi, -np.pi, 1e-9, 1e12))
def test_explicit_fast_hermite_function(x):
    """Test that hard-coded (up to n=20) fast C hermite implementation cases are
    correct.

    For n > 20, the recursive relation is used in the cymath implementation so no need
    to test above this limit.
    """
    ns = np.arange(21)

    expected = scs.eval_hermite(ns, x)
    computed = [cymath.math.hermite(n, x) for n in ns]

    assert_allclose(expected, computed)


def test_factorial_lookup_table():
    """Test that look-up table for factorials is correct up to n = 20."""
    ns = np.arange(21)

    expected = scs.factorial(ns)
    computed = [cymath.math.factorial(n) for n in ns]

    assert_allclose(expected, computed)


def test_sqrt_factorial_lookup_table():
    """Test that look-up table for sqrt(factorials) is correct up to n = 20."""
    ns = np.arange(21)

    expected = np.sqrt(scs.factorial(ns))
    computed = [cymath.math.sqrt_factorial(n) for n in ns]

    assert_allclose(expected, computed)
