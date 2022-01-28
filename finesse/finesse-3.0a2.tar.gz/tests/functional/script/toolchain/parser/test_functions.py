import pytest
from finesse.script.containers import KatScript, KatFunction, KatKwarg
from .....util import dedent_multiline
from ..util import (
    SPACE,
    COMMA,
    NEWLINE,
    NAME,
    NUMBER,
    EQUALS,
    LPAREN,
    RPAREN,
    COMMENT,
)


@pytest.mark.parametrize(
    "script,function",
    (
        (
            # Function with 4 positional arguments.
            "fake_function(1, 2, 3, 4)",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    NUMBER(1, 15, "1"),
                    NUMBER(1, 18, "2"),
                    NUMBER(1, 21, "3"),
                    NUMBER(1, 24, "4"),
                ],
                extra=[
                    LPAREN(1, 14),
                    COMMA(1, 16),
                    SPACE(1, 17),
                    COMMA(1, 19),
                    SPACE(1, 20),
                    COMMA(1, 22),
                    SPACE(1, 23),
                    RPAREN(1, 25),
                ],
            ),
        ),
        (
            # Function with 2 positional arguments and 2 keyword arguments.
            "fake_function(1, 2, c=3, d=4)",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    NUMBER(1, 15, "1"),
                    NUMBER(1, 18, "2"),
                    KatKwarg(
                        key=NAME(1, 21, "c"),
                        value=NUMBER(1, 23, "3"),
                        extra=[EQUALS(1, 22)],
                    ),
                    KatKwarg(
                        key=NAME(1, 26, "d"),
                        value=NUMBER(1, 28, "4"),
                        extra=[EQUALS(1, 27)],
                    ),
                ],
                extra=[
                    LPAREN(1, 14),
                    COMMA(1, 16),
                    SPACE(1, 17),
                    COMMA(1, 19),
                    SPACE(1, 20),
                    COMMA(1, 24),
                    SPACE(1, 25),
                    RPAREN(1, 29),
                ],
            ),
        ),
        (
            # Function with 4 keyword arguments.
            "fake_function(a=1, b=2, c=3, d=4)",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    KatKwarg(
                        key=NAME(1, 15, "a"),
                        value=NUMBER(1, 17, "1"),
                        extra=[EQUALS(1, 16)],
                    ),
                    KatKwarg(
                        key=NAME(1, 20, "b"),
                        value=NUMBER(1, 22, "2"),
                        extra=[EQUALS(1, 21)],
                    ),
                    KatKwarg(
                        key=NAME(1, 25, "c"),
                        value=NUMBER(1, 27, "3"),
                        extra=[EQUALS(1, 26)],
                    ),
                    KatKwarg(
                        key=NAME(1, 30, "d"),
                        value=NUMBER(1, 32, "4"),
                        extra=[EQUALS(1, 31)],
                    ),
                ],
                extra=[
                    LPAREN(1, 14),
                    COMMA(1, 18),
                    SPACE(1, 19),
                    COMMA(1, 23),
                    SPACE(1, 24),
                    COMMA(1, 28),
                    SPACE(1, 29),
                    RPAREN(1, 33),
                ],
            ),
        ),
        # Trailing comma.
        pytest.param(
            "fake_function(1,)",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[NUMBER(1, 15, "1"),],
                extra=[LPAREN(1, 14), COMMA(1, 16), RPAREN(1, 17),],
            ),
            id="single-line-trailing-comma-arg-nospace",
        ),
        pytest.param(
            "fake_function(1 ,)",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[NUMBER(1, 15, "1"),],
                extra=[LPAREN(1, 14), SPACE(1, 16), COMMA(1, 17), RPAREN(1, 18),],
            ),
            id="single-line-trailing-comma-arg-prespace",
        ),
        pytest.param(
            "fake_function(1, )",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[NUMBER(1, 15, "1"),],
                extra=[LPAREN(1, 14), COMMA(1, 16), SPACE(1, 17), RPAREN(1, 18),],
            ),
            id="single-line-trailing-comma-arg-postspace",
        ),
        pytest.param(
            "fake_function(1 , )",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[NUMBER(1, 15, "1"),],
                extra=[
                    LPAREN(1, 14),
                    SPACE(1, 16),
                    COMMA(1, 17),
                    SPACE(1, 18),
                    RPAREN(1, 19),
                ],
            ),
            id="single-line-trailing-comma-arg-prepostspace",
        ),
        pytest.param(
            "fake_function(a=1,)",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    KatKwarg(
                        key=NAME(1, 15, "a"),
                        value=NUMBER(1, 17, "1"),
                        extra=[EQUALS(1, 16)],
                    ),
                ],
                extra=[LPAREN(1, 14), COMMA(1, 18), RPAREN(1, 19),],
            ),
            id="single-line-trailing-comma-kwarg-nospace",
        ),
        pytest.param(
            "fake_function(a=1 ,)",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    KatKwarg(
                        key=NAME(1, 15, "a"),
                        value=NUMBER(1, 17, "1"),
                        extra=[EQUALS(1, 16)],
                    ),
                ],
                extra=[LPAREN(1, 14), SPACE(1, 18), COMMA(1, 19), RPAREN(1, 20),],
            ),
            id="single-line-trailing-comma-kwarg-prespace",
        ),
        pytest.param(
            "fake_function(a=1, )",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    KatKwarg(
                        key=NAME(1, 15, "a"),
                        value=NUMBER(1, 17, "1"),
                        extra=[EQUALS(1, 16)],
                    ),
                ],
                extra=[LPAREN(1, 14), COMMA(1, 18), SPACE(1, 19), RPAREN(1, 20),],
            ),
            id="single-line-trailing-comma-kwarg-postspace",
        ),
        pytest.param(
            "fake_function(a=1 , )",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    KatKwarg(
                        key=NAME(1, 15, "a"),
                        value=NUMBER(1, 17, "1"),
                        extra=[EQUALS(1, 16)],
                    ),
                ],
                extra=[
                    LPAREN(1, 14),
                    SPACE(1, 18),
                    COMMA(1, 19),
                    SPACE(1, 20),
                    RPAREN(1, 21),
                ],
            ),
            id="single-line-trailing-comma-kwarg-prepostspace",
        ),
        pytest.param(
            "fake_function(1, b=2 , )",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    NUMBER(1, 15, "1"),
                    KatKwarg(
                        key=NAME(1, 18, "b"),
                        value=NUMBER(1, 20, "2"),
                        extra=[EQUALS(1, 19)],
                    ),
                ],
                extra=[
                    LPAREN(1, 14),
                    COMMA(1, 16),
                    SPACE(1, 17),
                    SPACE(1, 21),
                    COMMA(1, 22),
                    SPACE(1, 23),
                    RPAREN(1, 24),
                ],
            ),
            id="single-line-trailing-comma-arg-kwarg-prepostspace",
        ),
    ),
)
def test_single_line(parser, script, function):
    """Single line function."""
    assert parser.parse(script) == KatScript(arguments=[function], extra=[])


@pytest.mark.parametrize(
    "script,function",
    (
        (
            dedent_multiline(
                """
                fake_function(
                    1, 2, 3, 4
                )
                """
            ),
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    NUMBER(2, 5, "1"),
                    NUMBER(2, 8, "2"),
                    NUMBER(2, 11, "3"),
                    NUMBER(2, 14, "4"),
                ],
                extra=[
                    LPAREN(1, 14),
                    NEWLINE(1, 15),
                    SPACE(2, 1, 4),
                    COMMA(2, 6),
                    SPACE(2, 7),
                    COMMA(2, 9),
                    SPACE(2, 10),
                    COMMA(2, 12),
                    SPACE(2, 13),
                    NEWLINE(2, 15),
                    RPAREN(3, 1),
                ],
            ),
        ),
        (
            dedent_multiline(
                """
                fake_function(
                    1,
                    2,
                    a=3,
                    b=4
                )
                """
            ),
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[
                    NUMBER(2, 5, "1"),
                    NUMBER(3, 5, "2"),
                    KatKwarg(
                        key=NAME(4, 5, "a"),
                        value=NUMBER(4, 7, "3"),
                        extra=[EQUALS(4, 6)],
                    ),
                    KatKwarg(
                        key=NAME(5, 5, "b"),
                        value=NUMBER(5, 7, "4"),
                        extra=[EQUALS(5, 6)],
                    ),
                ],
                extra=[
                    LPAREN(1, 14),
                    NEWLINE(1, 15),
                    SPACE(2, 1, 4),
                    COMMA(2, 6),
                    NEWLINE(2, 7),
                    SPACE(3, 1, 4),
                    COMMA(3, 6),
                    NEWLINE(3, 7),
                    SPACE(4, 1, 4),
                    COMMA(4, 8),
                    NEWLINE(4, 9),
                    SPACE(5, 1, 4),
                    NEWLINE(5, 8),
                    RPAREN(6, 1),
                ],
            ),
        ),
        # Trailing comma.
        pytest.param(
            dedent_multiline(
                """
                fake_function(
                    1,
                    # 2,
                )
                """
            ),
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[NUMBER(2, 5, "1")],
                extra=[
                    LPAREN(1, 14),
                    NEWLINE(1, 15),
                    SPACE(2, 1, 4),
                    COMMA(2, 6),
                    NEWLINE(2, 7),
                    SPACE(3, 1, 4),
                    COMMENT(3, 5, "# 2,"),
                    NEWLINE(3, 9),
                    RPAREN(4, 1),
                ],
            ),
            id="multi-line-trailing-comma",
        ),
    ),
)
def test_multi_line(parser, script, function):
    """Multi-line function."""
    assert parser.parse(script) == KatScript(arguments=[function], extra=[])


@pytest.mark.parametrize(
    "script,function",
    (
        (
            "fake_function()",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[],
                extra=[LPAREN(1, 14), RPAREN(1, 15)],
            ),
        ),
        (
            "fake_function( )",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[],
                extra=[LPAREN(1, 14), SPACE(1, 15), RPAREN(1, 16)],
            ),
        ),
        (
            "fake_function(  )",
            KatFunction(
                directive=NAME(1, 1, "fake_function"),
                arguments=[],
                extra=[LPAREN(1, 14), SPACE(1, 15, 2), RPAREN(1, 17)],
            ),
        ),
    ),
)
def test_empty_arguments(parser, script, function):
    assert parser.parse(script) == KatScript(arguments=[function], extra=[])


@pytest.mark.parametrize(
    "script,function",
    (
        (
            # Nested statement without parameters.
            dedent_multiline(
                """
                fake_analysis(
                    nested1(
                        1, 2
                    ),
                    nested2(
                        3, 4
                    ),
                    on_complete=subanalysis()
                )
                """
            ),
            KatFunction(
                directive=NAME(1, 1, "fake_analysis"),
                arguments=[
                    KatFunction(
                        directive=NAME(2, 5, "nested1"),
                        arguments=[NUMBER(3, 9, "1"), NUMBER(3, 12, "2"),],
                        extra=[
                            LPAREN(2, 12),
                            NEWLINE(2, 13),
                            SPACE(3, 1, 8),
                            COMMA(3, 10),
                            SPACE(3, 11),
                            NEWLINE(3, 13),
                            SPACE(4, 1, 4),
                            RPAREN(4, 5),
                        ],
                    ),
                    KatFunction(
                        directive=NAME(5, 5, "nested2"),
                        arguments=[NUMBER(6, 9, "3"), NUMBER(6, 12, "4"),],
                        extra=[
                            LPAREN(5, 12),
                            NEWLINE(5, 13),
                            SPACE(6, 1, 8),
                            COMMA(6, 10),
                            SPACE(6, 11),
                            NEWLINE(6, 13),
                            SPACE(7, 1, 4),
                            RPAREN(7, 5),
                        ],
                    ),
                    KatKwarg(
                        key=NAME(8, 5, "on_complete"),
                        value=KatFunction(
                            directive=NAME(8, 17, "subanalysis"),
                            arguments=[],
                            extra=[LPAREN(8, 28), RPAREN(8, 29)],
                        ),
                        extra=[EQUALS(8, 16)],
                    ),
                ],
                extra=[
                    LPAREN(1, 14),
                    NEWLINE(1, 15),
                    SPACE(2, 1, 4),
                    COMMA(4, 6),
                    NEWLINE(4, 7),
                    SPACE(5, 1, 4),
                    COMMA(7, 6),
                    NEWLINE(7, 7),
                    SPACE(8, 1, 4),
                    NEWLINE(8, 30),
                    RPAREN(9, 1),
                ],
            ),
        ),
    ),
)
def test_nested(parser, script, function):
    assert parser.parse(script) == KatScript(arguments=[function], extra=[])
