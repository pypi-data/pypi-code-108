import pytest
from finesse.script.containers import KatScript, KatElement
from finesse.script.exceptions import KatScriptError
from ..util import NAME, NUMBER, SPACE
from ..data import SI_PREFICES, INTEGERS, FLOATS, IMAGINARIES


@pytest.mark.parametrize("number,_a,_b", INTEGERS + FLOATS + IMAGINARIES)
def test_number(parser, number, _a, _b):
    assert parser.parse(f"fake_element el1 {number}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[NUMBER(1, 18, number)],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


def test_numbers_with_float_exponents_are_invalid(parser):
    """Test that numbers with float exponents are invalid.

    Only integer exponents are allowed by Python's :func:`float`.
    """
    with pytest.raises(KatScriptError):
        parser.parse("fake_element el1 3.141e2.2")


@pytest.mark.parametrize("prefix,exponent", SI_PREFICES.items())
def test_numbers_with_si_prefices(parser, prefix, exponent):
    strval = f"3.141e{exponent}"
    assert parser.parse(f"fake_element el1 {strval}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[NUMBER(1, 18, strval)],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize("prefix", SI_PREFICES)
def test_numbers_with_si_prefices_and_scientific_notation_invalid__first(
    parser, prefix
):
    """Test that numbers with SI prefices and scientific notation together are invalid."""
    with pytest.raises(KatScriptError):
        parser.parse(f"fake_element el1 3.141{prefix}e-6")


@pytest.mark.parametrize("prefix", SI_PREFICES)
def test_numbers_with_scientific_exponents_and_si_prefices_invalid(parser, prefix):
    """Test that numbers with both scientific exponents and SI prefices are invalid."""
    with pytest.raises(KatScriptError):
        parser.parse(f"fake_element el1 3.141e-2{prefix}")


@pytest.mark.parametrize("prefix", SI_PREFICES)
def test_numbers_with_si_prefices_and_scientific_notation_invalid__second(
    parser, prefix
):
    """Test that numbers with SI prefices and scientific notation together are invalid."""
    with pytest.raises(KatScriptError):
        parser.parse(f"fake_element el1 3.141e-6{prefix}")


@pytest.mark.parametrize("fakeprefix", ("mm", "nn", "pp", "z", "o", "l", "r", "i"))
def test_numbers_with_invalid_si_prefices_invalid(parser, fakeprefix):
    """Test that numbers with invalid SI prefices cause an error."""
    # Note: we can't search the error message for exact token because e.g. 'pp' will match 'p'.
    with pytest.raises(KatScriptError):
        parser.parse(f"fake_element el1 3.141{fakeprefix}")
