"""Array parser tests.

Note that expression arrays are tested in `test_expressions.py`.
"""

import pytest
from finesse.script.containers import KatScript, KatElement, KatArray
from finesse.script.exceptions import KatScriptError
from ..util import (
    NAME,
    BOOLEAN,
    NUMBER,
    STRING,
    NONE,
    SPACE,
    COMMA,
    LBRACKET,
    RBRACKET,
)
from ..data import SI_PREFICES, INTEGERS, FLOATS, IMAGINARIES, STRINGS, BOOLEANS
from .....util import escape_full


@pytest.mark.parametrize(
    "string,array",
    (
        # Empty.
        ("[]", KatArray(arguments=[], extra=[LBRACKET(1, 18), RBRACKET(1, 19)])),
        (
            "[[]]",
            KatArray(
                arguments=[
                    KatArray(arguments=[], extra=[LBRACKET(1, 19), RBRACKET(1, 20)])
                ],
                extra=[LBRACKET(1, 18), RBRACKET(1, 21)],
            ),
        ),
        (
            "[[[]]]",
            KatArray(
                arguments=[
                    KatArray(
                        arguments=[
                            KatArray(
                                arguments=[], extra=[LBRACKET(1, 20), RBRACKET(1, 21)]
                            )
                        ],
                        extra=[LBRACKET(1, 19), RBRACKET(1, 22)],
                    )
                ],
                extra=[LBRACKET(1, 18), RBRACKET(1, 23)],
            ),
        ),
        (
            "[ [ [ ]]]",
            KatArray(
                arguments=[
                    KatArray(
                        arguments=[
                            KatArray(
                                arguments=[],
                                extra=[LBRACKET(1, 22), SPACE(1, 23), RBRACKET(1, 24)],
                            )
                        ],
                        extra=[LBRACKET(1, 20), SPACE(1, 21), RBRACKET(1, 25)],
                    )
                ],
                extra=[LBRACKET(1, 18), SPACE(1, 19), RBRACKET(1, 26)],
            ),
        ),
        (
            "[1, [[]]]",
            KatArray(
                arguments=[
                    NUMBER(1, 19, "1"),
                    KatArray(
                        arguments=[
                            KatArray(
                                arguments=[], extra=[LBRACKET(1, 23), RBRACKET(1, 24)]
                            )
                        ],
                        extra=[LBRACKET(1, 22), RBRACKET(1, 25)],
                    ),
                ],
                extra=[LBRACKET(1, 18), COMMA(1, 20), SPACE(1, 21), RBRACKET(1, 26)],
            ),
        ),
        (
            "[1, [[], 2]]",
            KatArray(
                arguments=[
                    NUMBER(1, 19, "1"),
                    KatArray(
                        arguments=[
                            KatArray(
                                arguments=[], extra=[LBRACKET(1, 23), RBRACKET(1, 24)]
                            ),
                            NUMBER(1, 27, "2"),
                        ],
                        extra=[
                            LBRACKET(1, 22),
                            COMMA(1, 25),
                            SPACE(1, 26),
                            RBRACKET(1, 28),
                        ],
                    ),
                ],
                extra=[LBRACKET(1, 18), COMMA(1, 20), SPACE(1, 21), RBRACKET(1, 29)],
            ),
        ),
        (
            "[0, 0]",
            KatArray(
                arguments=[NUMBER(1, 19, "0"), NUMBER(1, 22, "0")],
                extra=[LBRACKET(1, 18), COMMA(1, 20), SPACE(1, 21), RBRACKET(1, 23)],
            ),
        ),
        (
            "[[1, 0], [0, 1], [0, 2]]",
            KatArray(
                arguments=[
                    KatArray(
                        arguments=[NUMBER(1, 20, "1"), NUMBER(1, 23, "0")],
                        extra=[
                            LBRACKET(1, 19),
                            COMMA(1, 21),
                            SPACE(1, 22),
                            RBRACKET(1, 24),
                        ],
                    ),
                    KatArray(
                        arguments=[NUMBER(1, 28, "0"), NUMBER(1, 31, "1")],
                        extra=[
                            LBRACKET(1, 27),
                            COMMA(1, 29),
                            SPACE(1, 30),
                            RBRACKET(1, 32),
                        ],
                    ),
                    KatArray(
                        arguments=[NUMBER(1, 36, "0"), NUMBER(1, 39, "2")],
                        extra=[
                            LBRACKET(1, 35),
                            COMMA(1, 37),
                            SPACE(1, 38),
                            RBRACKET(1, 40),
                        ],
                    ),
                ],
                extra=[
                    LBRACKET(1, 18),
                    COMMA(1, 25),
                    SPACE(1, 26),
                    COMMA(1, 33),
                    SPACE(1, 34),
                    RBRACKET(1, 41),
                ],
            ),
        ),
        (
            "[[1, 0], [[0, 1]], [[0, 2]]]",
            KatArray(
                arguments=[
                    KatArray(
                        arguments=[NUMBER(1, 20, "1"), NUMBER(1, 23, "0")],
                        extra=[
                            LBRACKET(1, 19),
                            COMMA(1, 21),
                            SPACE(1, 22),
                            RBRACKET(1, 24),
                        ],
                    ),
                    KatArray(
                        arguments=[
                            KatArray(
                                arguments=[NUMBER(1, 29, "0"), NUMBER(1, 32, "1")],
                                extra=[
                                    LBRACKET(1, 28),
                                    COMMA(1, 30),
                                    SPACE(1, 31),
                                    RBRACKET(1, 33),
                                ],
                            )
                        ],
                        extra=[LBRACKET(1, 27), RBRACKET(1, 34)],
                    ),
                    KatArray(
                        arguments=[
                            KatArray(
                                arguments=[NUMBER(1, 39, "0"), NUMBER(1, 42, "2")],
                                extra=[
                                    LBRACKET(1, 38),
                                    COMMA(1, 40),
                                    SPACE(1, 41),
                                    RBRACKET(1, 43),
                                ],
                            )
                        ],
                        extra=[LBRACKET(1, 37), RBRACKET(1, 44)],
                    ),
                ],
                extra=[
                    LBRACKET(1, 18),
                    COMMA(1, 25),
                    SPACE(1, 26),
                    COMMA(1, 35),
                    SPACE(1, 36),
                    RBRACKET(1, 45),
                ],
            ),
        ),
        # Trailing comma.
        pytest.param(
            "[1,]",
            KatArray(
                arguments=[NUMBER(1, 19, "1")],
                extra=[LBRACKET(1, 18), COMMA(1, 20), RBRACKET(1, 21)],
            ),
            id="single-line-trailing-comma-nospace",
        ),
        pytest.param(
            "[1 ,]",
            KatArray(
                arguments=[NUMBER(1, 19, "1")],
                extra=[LBRACKET(1, 18), SPACE(1, 20), COMMA(1, 21), RBRACKET(1, 22)],
            ),
            id="single-line-trailing-comma-prespace",
        ),
        pytest.param(
            "[1, ]",
            KatArray(
                arguments=[NUMBER(1, 19, "1")],
                extra=[LBRACKET(1, 18), COMMA(1, 20), SPACE(1, 21), RBRACKET(1, 22)],
            ),
            id="single-line-trailing-comma-postspace",
        ),
        pytest.param(
            "[1 , ]",
            KatArray(
                arguments=[NUMBER(1, 19, "1")],
                extra=[
                    LBRACKET(1, 18),
                    SPACE(1, 20),
                    COMMA(1, 21),
                    SPACE(1, 22),
                    RBRACKET(1, 23),
                ],
            ),
            id="single-line-trailing-comma-prepostspace",
        ),
    ),
)
def test_array_single_line(parser, string, array):
    assert parser.parse(f"fake_element el1 {string}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[array],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize("number,_a,_b", INTEGERS + FLOATS + IMAGINARIES)
def test_array_numbers(parser, number, _a, _b):
    """Test that numbers as array values parse correctly."""
    assert parser.parse(f"fake_element el1 [{number}]") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[
                    KatArray(
                        arguments=[NUMBER(1, 19, number)],
                        extra=[LBRACKET(1, 18), RBRACKET(1, 19 + len(number))],
                    ),
                ],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize("prefix,_", SI_PREFICES.items())
def test_array_si_prefix_values(parser, prefix, _):
    """Test that numbers with SI prefices as array values parse correctly."""
    number = f"3.141{prefix}"
    assert parser.parse(f"fake_element el1 [{number}]") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[
                    KatArray(
                        arguments=[NUMBER(1, 19, number)],
                        extra=[LBRACKET(1, 18), RBRACKET(1, 19 + len(number))],
                    ),
                ],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize("string,_a,_b", STRINGS)
def test_array_string_values(parser, string, _a, _b):
    assert parser.parse(f"fake_element el1 [{string}]") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[
                    KatArray(
                        arguments=[STRING(1, 19, string)],
                        extra=[LBRACKET(1, 18), RBRACKET(1, 19 + len(string))],
                    ),
                ],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


def test_array_empty_value(parser):
    assert parser.parse("fake_element el1 [none]") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[
                    KatArray(
                        arguments=[NONE(1, 19)],
                        extra=[LBRACKET(1, 18), RBRACKET(1, 19 + len("none"))],
                    ),
                ],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize("value,_a,_b", BOOLEANS)
def test_array_boolean_values(parser, value, _a, _b):
    assert parser.parse(f"fake_element el1 [{value}]") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[
                    KatArray(
                        arguments=[BOOLEAN(1, 19, value)],
                        extra=[LBRACKET(1, 18), RBRACKET(1, 19 + len(value))],
                    ),
                ],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize(
    "expression,error",
    (
        pytest.param(
            "[1 1]",
            (
                "\nline 1: array values should be delimited by ','\n"
                "-->1: fake_element el1 [1 1]\n"
                "                         ^"
            ),
            id="no-comma",
        ),
        pytest.param(
            "[1, 1 1]",
            (
                "\nline 1: array values should be delimited by ','\n"
                "-->1: fake_element el1 [1, 1 1]\n"
                "                            ^"
            ),
            id="no-second-comma",
        ),
        pytest.param(
            "[1, (1) 1]",
            (
                "\nline 1: array values should be delimited by ','\n"
                "-->1: fake_element el1 [1, (1) 1]\n"
                "                              ^"
            ),
            id="no-second-comma-expr",
        ),
    ),
)
def test_invalid_syntax(parser, expression, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        parser.parse(f"fake_element el1 {expression}")
