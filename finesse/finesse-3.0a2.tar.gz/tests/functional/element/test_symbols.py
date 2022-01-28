"""Symbol unit tests."""

import math
from finesse import constants
from finesse.symbols import FUNCTIONS, CONSTANTS, Constant


def test_symbols_with_numbers():
    """Test that symbol expressions with numbers evaluate to the correct values."""
    assert (Constant(3.141) + Constant(3.141)).eval() == 6.282
    assert (Constant(3.141) - Constant(3.141)).eval() == 0
    assert (Constant(3.141) * Constant(10)).eval() == 31.41
    assert (Constant(3.141) / Constant(10)).eval() == 0.3141


def test_symbols_with_constants():
    """Test that symbol expressions with constants evaluate to the correct values."""
    assert CONSTANTS["pi"].eval() == constants.PI
    assert CONSTANTS["c0"].eval() == constants.C_LIGHT


def test_symbols_with_functions__single():
    """Test that symbol expressions with single parameter functions evaluate to the
    correct values."""
    assert FUNCTIONS["cos"](0).eval() == 1
    assert FUNCTIONS["cos"](CONSTANTS["pi"]).eval() == -1

    # abs_tol required because math.isclose(anything, 0) is always False by default.
    assert math.isclose(FUNCTIONS["cos"](CONSTANTS["pi"] / 2).eval(), 0, abs_tol=1e-15)
    assert math.isclose(
        FUNCTIONS["cos"](3 * CONSTANTS["pi"] / 2).eval(), 0, abs_tol=1e-15
    )
    assert math.isclose(FUNCTIONS["exp"](1j * CONSTANTS["pi"]).eval().real, -1)


def test_symbols_with_functions__multiple():
    """Test that symbol expressions with multiple parameter functions evaluate to the
    correct values."""
    assert FUNCTIONS["arctan2"](Constant(0), Constant(0)).eval() == 0
    assert FUNCTIONS["arctan2"](Constant(1), Constant(1)).eval() == constants.PI / 4
    assert (
        FUNCTIONS["arctan2"](CONSTANTS["pi"], CONSTANTS["pi"]).eval()
        == constants.PI / 4
    )
    assert (
        FUNCTIONS["arctan2"](Constant(1.23e-5), Constant(6.43e-7)).eval()
        == 1.518567446860085
    )


def test_symbols_with_nested_functions():
    """Test that symbol expressions with nested functions evaluate to the correct
    values."""
    assert FUNCTIONS["arccos"](FUNCTIONS["cos"](CONSTANTS["pi"])).eval() == constants.PI
    assert (
        FUNCTIONS["arcsin"](FUNCTIONS["sin"](CONSTANTS["pi"] / 2)).eval()
        == constants.PI / 2
    )
    # sin²(theta) = (1 - cos(2 theta)) / 2
    assert math.isclose(
        (Constant(1) - FUNCTIONS["cos"](Constant(2) * Constant(8.8)))
        / Constant(2).eval(),
        math.sin(8.8) ** 2,
    )
