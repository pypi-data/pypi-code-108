"""Kat compiler expression unit tests."""

import pytest
from finesse.script import parse
from .....util import dedent_multiline
from ..data import (
    EAGER_EXPRESSIONS,
    EAGER_EXPRESSIONS_COMPLEX as _EAGER_EXPRESSIONS_COMPLEX,
    LAZY_EXPRESSIONS,
)


# Only use positive complex numbers for parser tests because the parameter used in the tests (a q
# parameter) doesn't allow negative numbers.
EAGER_EXPRESSIONS_COMPLEX = (
    (script, expected)
    for script, expected in _EAGER_EXPRESSIONS_COMPLEX
    if expected.imag > 0 and expected.imag != float("inf")
)


@pytest.mark.parametrize("expression,expected", EAGER_EXPRESSIONS)
def test_expressions_eager(expression, expected):
    """Expressions that should be eagerly evaluated."""
    model = parse(f"var myvar {expression}")
    assert model.myvar.value.value == expected


@pytest.mark.parametrize("expression,expected", EAGER_EXPRESSIONS_COMPLEX)
def test_expressions_eager_complex(expression, expected):
    """Complex expressions that should be eagerly evaluated."""
    model = parse(
        f"""
        laser l1
        gauss mygauss l1.p1.o q={expression}
        """
    )
    model.mygauss.qx.q == pytest.approx(expected)


@pytest.mark.parametrize("expression,expected", LAZY_EXPRESSIONS)
def test_expressions_lazy(expression, expected):
    """Expressions that should be lazily evaluated."""
    model = parse(f"var myvar {expression}")
    assert model.myvar.value.value == expected


@pytest.mark.parametrize(
    "script,attr,expected",
    (
        (
            dedent_multiline(
                """
                var order 2
                modulator mod1 10M 0.1 1+&order
                """
            ),
            "mod1.order",
            3,
        ),
    ),
)
def test_expressions_with_info_parameter_arguments(script, attr, expected):
    """Test that info parameter arguments can be referenced in expressions.

    See #130 and !57.
    """
    model = parse(script)
    assert model.get(attr).eval() == expected
