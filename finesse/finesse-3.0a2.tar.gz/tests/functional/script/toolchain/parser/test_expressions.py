import pytest
from finesse.script.containers import (
    KatScript,
    KatElement,
    KatFunction,
    KatExpression,
    KatGroupedExpression,
    KatNumericalArray,
)
from ..util import (
    NAME,
    NUMBER,
    SPACE,
    COMMA,
    PLUS,
    MINUS,
    TIMES,
    DIVIDE,
    FLOORDIVIDE,
    POWER,
    LPAREN,
    RPAREN,
    LBRACKET,
    RBRACKET,
)


@pytest.mark.parametrize(
    "expression,expected",
    (
        (
            "1+2",
            KatExpression(
                operator=PLUS(1, 19),
                arguments=[NUMBER(1, 18, "1"), NUMBER(1, 20, "2")],
                extra=[],
            ),
        ),
        (
            "3.6-2.2",
            KatExpression(
                operator=MINUS(1, 21),
                arguments=[NUMBER(1, 18, "3.6"), NUMBER(1, 22, "2.2")],
                extra=[],
            ),
        ),
        (
            "3.141*10",
            KatExpression(
                operator=TIMES(1, 23),
                arguments=[NUMBER(1, 18, "3.141"), NUMBER(1, 24, "10")],
                extra=[],
            ),
        ),
        (
            "5.04/1",
            KatExpression(
                operator=DIVIDE(1, 22),
                arguments=[NUMBER(1, 18, "5.04"), NUMBER(1, 23, "1")],
                extra=[],
            ),
        ),
        (
            "4//8.",
            KatExpression(
                operator=FLOORDIVIDE(1, 19),
                arguments=[NUMBER(1, 18, "4"), NUMBER(1, 21, "8.")],
                extra=[],
            ),
        ),
        (
            "8.4**3.0",
            KatExpression(
                operator=POWER(1, 21),
                arguments=[NUMBER(1, 18, "8.4"), NUMBER(1, 23, "3.0")],
                extra=[],
            ),
        ),
    ),
)
def test_binary_expression(parser, expression, expected):
    assert parser.parse(f"fake_element el1 {expression}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[expected],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize(
    "expression,expected",
    (
        (
            "1+2+3",
            KatExpression(
                operator=PLUS(1, 21),
                arguments=[
                    KatExpression(
                        operator=PLUS(1, 19),
                        arguments=[NUMBER(1, 18, "1"), NUMBER(1, 20, "2")],
                        extra=[],
                    ),
                    NUMBER(1, 22, "3"),
                ],
                extra=[],
            ),
        ),
        (
            "-1+2-3+4",
            KatExpression(
                operator=PLUS(1, 24),
                arguments=[
                    KatExpression(
                        operator=MINUS(1, 22),
                        arguments=[
                            KatExpression(
                                operator=PLUS(1, 20),
                                arguments=[
                                    KatFunction(
                                        directive=MINUS(1, 18),
                                        arguments=[NUMBER(1, 19, "1")],
                                        extra=[],
                                    ),
                                    NUMBER(1, 21, "2"),
                                ],
                                extra=[],
                            ),
                            NUMBER(1, 23, "3"),
                        ],
                        extra=[],
                    ),
                    NUMBER(1, 25, "4"),
                ],
                extra=[],
            ),
        ),
    ),
)
def test_nested_expression(parser, expression, expected):
    assert parser.parse(f"fake_element el1 {expression}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[expected],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize(
    "expression,expected",
    (
        (
            "(1)",
            KatGroupedExpression(
                arguments=[NUMBER(1, 19, "1")], extra=[LPAREN(1, 18), RPAREN(1, 20)]
            ),
        ),
        (
            "(((1)))",
            KatGroupedExpression(
                arguments=[
                    KatGroupedExpression(
                        arguments=[
                            KatGroupedExpression(
                                arguments=[NUMBER(1, 21, "1")],
                                extra=[LPAREN(1, 20), RPAREN(1, 22)],
                            ),
                        ],
                        extra=[LPAREN(1, 19), RPAREN(1, 23)],
                    ),
                ],
                extra=[LPAREN(1, 18), RPAREN(1, 24)],
            ),
        ),
        (
            "(((((1)))))",
            KatGroupedExpression(
                arguments=[
                    KatGroupedExpression(
                        arguments=[
                            KatGroupedExpression(
                                arguments=[
                                    KatGroupedExpression(
                                        arguments=[
                                            KatGroupedExpression(
                                                arguments=[NUMBER(1, 23, "1")],
                                                extra=[LPAREN(1, 22), RPAREN(1, 24)],
                                            ),
                                        ],
                                        extra=[LPAREN(1, 21), RPAREN(1, 25)],
                                    ),
                                ],
                                extra=[LPAREN(1, 20), RPAREN(1, 26)],
                            ),
                        ],
                        extra=[LPAREN(1, 19), RPAREN(1, 27)],
                    ),
                ],
                extra=[LPAREN(1, 18), RPAREN(1, 28)],
            ),
        ),
    ),
)
def test_parentheses(parser, expression, expected):
    assert parser.parse(f"fake_element el1 {expression}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[expected],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize(
    "expression,expected",
    (
        # Standard precendence.
        (
            "2+3*4",
            KatExpression(
                operator=PLUS(1, 19),
                arguments=[
                    NUMBER(1, 18, "2"),
                    KatExpression(
                        operator=TIMES(1, 21),
                        arguments=[NUMBER(1, 20, "3"), NUMBER(1, 22, "4")],
                        extra=[],
                    ),
                ],
                extra=[],
            ),
        ),
        (
            "3*4+2",
            KatExpression(
                operator=PLUS(1, 21),
                arguments=[
                    KatExpression(
                        operator=TIMES(1, 19),
                        arguments=[NUMBER(1, 18, "3"), NUMBER(1, 20, "4")],
                        extra=[],
                    ),
                    NUMBER(1, 22, "2"),
                ],
                extra=[],
            ),
        ),
        (
            "3+5**2",
            KatExpression(
                operator=PLUS(1, 19),
                arguments=[
                    NUMBER(1, 18, "3"),
                    KatExpression(
                        operator=POWER(1, 21),
                        arguments=[NUMBER(1, 20, "5"), NUMBER(1, 23, "2"),],
                        extra=[],
                    ),
                ],
                extra=[],
            ),
        ),
        (
            "4**3**2",
            KatExpression(
                operator=POWER(1, 19),
                arguments=[
                    NUMBER(1, 18, "4"),
                    KatExpression(
                        operator=POWER(1, 22),
                        arguments=[NUMBER(1, 21, "3"), NUMBER(1, 24, "2")],
                        extra=[],
                    ),
                ],
                extra=[],
            ),
        ),
        (
            "10/5/2",
            KatExpression(
                operator=DIVIDE(1, 22),
                arguments=[
                    KatExpression(
                        operator=DIVIDE(1, 20),
                        arguments=[NUMBER(1, 18, "10"), NUMBER(1, 21, "5")],
                        extra=[],
                    ),
                    NUMBER(1, 23, "2"),
                ],
                extra=[],
            ),
        ),
        # Bracket-enforced precendence.
        (
            "(3*5)**2",
            KatExpression(
                operator=POWER(1, 23),
                arguments=[
                    KatGroupedExpression(
                        arguments=[
                            KatExpression(
                                operator=TIMES(1, 20),
                                arguments=[NUMBER(1, 19, "3"), NUMBER(1, 21, "5")],
                                extra=[],
                            ),
                        ],
                        extra=[LPAREN(1, 18), RPAREN(1, 22)],
                    ),
                    NUMBER(1, 25, "2"),
                ],
                extra=[],
            ),
        ),
        (
            "(2+3)*4",
            KatExpression(
                operator=TIMES(1, 23),
                arguments=[
                    KatGroupedExpression(
                        arguments=[
                            KatExpression(
                                operator=PLUS(1, 20),
                                arguments=[NUMBER(1, 19, "2"), NUMBER(1, 21, "3")],
                                extra=[],
                            ),
                        ],
                        extra=[LPAREN(1, 18), RPAREN(1, 22)],
                    ),
                    NUMBER(1, 24, "4"),
                ],
                extra=[],
            ),
        ),
        (
            "(4**3)**2",
            KatExpression(
                operator=POWER(1, 24),
                arguments=[
                    KatGroupedExpression(
                        arguments=[
                            KatExpression(
                                operator=POWER(1, 20),
                                arguments=[NUMBER(1, 19, "4"), NUMBER(1, 22, "3")],
                                extra=[],
                            ),
                        ],
                        extra=[LPAREN(1, 18), RPAREN(1, 23)],
                    ),
                    NUMBER(1, 26, "2"),
                ],
                extra=[],
            ),
        ),
        (
            "10/(5/2)",
            KatExpression(
                operator=DIVIDE(1, 20),
                arguments=[
                    NUMBER(1, 18, "10"),
                    KatGroupedExpression(
                        arguments=[
                            KatExpression(
                                operator=DIVIDE(1, 23),
                                arguments=[NUMBER(1, 22, "5"), NUMBER(1, 24, "2")],
                                extra=[],
                            ),
                        ],
                        extra=[LPAREN(1, 21), RPAREN(1, 25)],
                    ),
                ],
                extra=[],
            ),
        ),
    ),
)
def test_precendence(parser, expression, expected):
    assert parser.parse(f"fake_element el1 {expression}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[expected],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize(
    "sign,expression",
    (
        # Integers.
        ("+", "0"),
        ("-", "0"),
        ("+", "15"),
        ("-", "15"),
        ("+", "50505"),
        ("-", "50505"),
        ## Long.
        ("+", "123141242151251616110"),
        ("-", "123141242151251616110"),
        # Floats.
        ("+", "0.0"),
        ("-", "0.0"),
        ("+", "15.151"),
        ("-", "15.151"),
        ## Scientific.
        ("+", "0.e7"),
        ("-", "0.e7"),
        ("+", "0.0e7"),
        ("-", "0.0e7"),
        ("+", "1.23e7"),
        ("-", "1.23e7"),
        ("+", "1.23e+7"),
        ("-", "1.23e+7"),
        ("+", "1.23e-7"),
        ("-", "1.23e-7"),
        ## Infinities.
        ("+", "inf"),
        ("-", "inf"),
        ## Imaginaries.
        ("+", "0j"),
        ("-", "0j"),
        ("+", "0.j"),
        ("-", "0.j"),
        ("+", "0.0j"),
        ("-", "0.0j"),
        ("+", "10j"),
        ("-", "10j"),
        ("+", "1.32j"),
        ("-", "1.32j"),
        ## Scientific.
        ("+", "0e7j"),
        ("-", "0e7j"),
        ("+", "0.e7j"),
        ("-", "0.e7j"),
        ("+", "0.0e7j"),
        ("-", "0.0e7j"),
        ("+", "1.23e7j"),
        ("-", "1.23e7j"),
        ("+", "1.23e+7j"),
        ("-", "1.23e+7j"),
        ("+", "1.23e-7j"),
        ("-", "1.23e-7j"),
        ## Infinities.
        ("+", "infj"),
        ("-", "infj"),
    ),
)
def test_unary_number(parser, sign, expression):
    """Test unary numbers.

    Unary numbers like -1 get parsed into the function MINUS(1). That means the number is always
    parsed without the sign and the sign determines the function (MINUS or PLUS).
    """
    assert parser.parse(f"fake_element el1 {sign}{expression}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[
                    KatFunction(
                        directive=MINUS(1, 18) if sign == "-" else PLUS(1, 18),
                        arguments=[NUMBER(1, 19, expression)],
                        extra=[],
                    ),
                ],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize(
    "expression,expected",
    (
        (
            # Empty functions parse instead as statements (via the `nestable_statement` production).
            # This is corrected in the build step.
            "a()",
            KatFunction(
                directive=NAME(1, 18, "a"),
                arguments=[],
                extra=[LPAREN(1, 19), RPAREN(1, 20)],
            ),
        ),
        (
            "a(3.141)",
            KatFunction(
                directive=NAME(1, 18, "a"),
                arguments=[NUMBER(1, 20, "3.141")],
                extra=[LPAREN(1, 19), RPAREN(1, 25)],
            ),
        ),
        (
            "b(1, 2, 3)",
            KatFunction(
                directive=NAME(1, 18, "b"),
                arguments=[NUMBER(1, 20, "1"), NUMBER(1, 23, "2"), NUMBER(1, 26, "3"),],
                extra=[
                    LPAREN(1, 19),
                    COMMA(1, 21),
                    SPACE(1, 22),
                    COMMA(1, 24),
                    SPACE(1, 25),
                    RPAREN(1, 27),
                ],
            ),
        ),
        (
            "a(a(a(1), 2), 3, 4)",
            KatFunction(
                directive=NAME(1, 18, "a"),
                arguments=[
                    KatFunction(
                        directive=NAME(1, 20, "a"),
                        arguments=[
                            KatFunction(
                                directive=NAME(1, 22, "a"),
                                arguments=[NUMBER(1, 24, "1")],
                                extra=[LPAREN(1, 23), RPAREN(1, 25)],
                            ),
                            NUMBER(1, 28, "2"),
                        ],
                        extra=[
                            LPAREN(1, 21),
                            COMMA(1, 26),
                            SPACE(1, 27),
                            RPAREN(1, 29),
                        ],
                    ),
                    NUMBER(1, 32, "3"),
                    NUMBER(1, 35, "4"),
                ],
                extra=[
                    LPAREN(1, 19),
                    COMMA(1, 30),
                    SPACE(1, 31),
                    COMMA(1, 33),
                    SPACE(1, 34),
                    RPAREN(1, 36),
                ],
            ),
        ),
    ),
)
def test_function(parser, expression, expected):
    assert parser.parse(f"fake_element el1 {expression}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[expected],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )


@pytest.mark.parametrize(
    "expression,expected",
    (
        (
            "2*[1, 2]",
            KatExpression(
                operator=TIMES(1, 19),
                arguments=[
                    NUMBER(1, 18, "2"),
                    KatNumericalArray(
                        arguments=[NUMBER(1, 21, "1"), NUMBER(1, 24, "2")],
                        extra=[
                            LBRACKET(1, 20),
                            COMMA(1, 22),
                            SPACE(1, 23),
                            RBRACKET(1, 25),
                        ],
                    ),
                ],
                extra=[],
            ),
        ),
        (
            "2*[1, 2/[3]]",
            KatExpression(
                operator=TIMES(1, 19),
                arguments=[
                    NUMBER(1, 18, "2"),
                    KatNumericalArray(
                        arguments=[
                            NUMBER(1, 21, "1"),
                            KatExpression(
                                operator=DIVIDE(1, 25),
                                arguments=[
                                    NUMBER(1, 24, "2"),
                                    KatNumericalArray(
                                        arguments=[NUMBER(1, 27, "3")],
                                        extra=[LBRACKET(1, 26), RBRACKET(1, 28)],
                                    ),
                                ],
                                extra=[],
                            ),
                        ],
                        extra=[
                            LBRACKET(1, 20),
                            COMMA(1, 22),
                            SPACE(1, 23),
                            RBRACKET(1, 29),
                        ],
                    ),
                ],
                extra=[],
            ),
        ),
    ),
)
def test_numerical_array(parser, expression, expected):
    assert parser.parse(f"fake_element el1 {expression}") == KatScript(
        arguments=[
            KatElement(
                directive=NAME(1, 1, "fake_element"),
                name=NAME(1, 14, "el1"),
                arguments=[expected],
                extra=[SPACE(1, 13), SPACE(1, 17)],
            )
        ],
        extra=[],
    )
