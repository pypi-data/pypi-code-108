"""Tests for the tokenizer without any normalization."""

import pytest
from .....util import dedent_multiline
from ..util import (
    NAME,
    NUMBER,
    STRING,
    BOOLEAN,
    PLUS,
    EQUALS,
    LPAREN,
    RPAREN,
    ENDMARKER,
    NEWLINE,
    SPACE,
    COMMENT,
    IMPLICITLINEEND,
)


def test_implicit_newline(tokenizer):
    """If there is no newline at the end of the script, an implicit newline is added."""
    assert list(tokenizer.tokenize("a")) == [
        NAME(1, 1, "a"),
        IMPLICITLINEEND(1, 2),
        ENDMARKER(2),
    ]


def test_explicit_newline(tokenizer):
    """If there is a newline at the end of the script, an implicit newline is NOT
    added."""
    assert list(tokenizer.tokenize("a\n")) == [
        NAME(1, 1, "a"),
        NEWLINE(1, 2),
        ENDMARKER(2),
    ]


@pytest.mark.parametrize(
    "string,expected",
    (
        ## Single line.
        (
            "1 + 1",
            [
                NUMBER(1, 1, "1"),
                SPACE(1, 2),
                PLUS(1, 3),
                SPACE(1, 4),
                NUMBER(1, 5, "1"),
                IMPLICITLINEEND(1, 6),
                ENDMARKER(2),
            ],
        ),
        ("true", [BOOLEAN(1, 1, "true"), IMPLICITLINEEND(1, 5), ENDMARKER(2),]),
        ("false", [BOOLEAN(1, 1, "false"), IMPLICITLINEEND(1, 6), ENDMARKER(2),]),
        (
            "a = ''",
            [
                NAME(1, 1, "a"),
                SPACE(1, 2),
                EQUALS(1, 3),
                SPACE(1, 4),
                STRING(1, 5, "''"),
                IMPLICITLINEEND(1, 7),
                ENDMARKER(2),
            ],
        ),
        (
            "a = 'foo'",
            [
                NAME(1, 1, "a"),
                SPACE(1, 2),
                EQUALS(1, 3),
                SPACE(1, 4),
                STRING(1, 5, "'foo'"),
                IMPLICITLINEEND(1, 10),
                ENDMARKER(2),
            ],
        ),
        (
            'a = "foo"',
            [
                NAME(1, 1, "a"),
                SPACE(1, 2),
                EQUALS(1, 3),
                SPACE(1, 4),
                STRING(1, 5, '"foo"'),
                IMPLICITLINEEND(1, 10),
                ENDMARKER(2),
            ],
        ),
        ("'\"'", [STRING(1, 1, "'\"'"), IMPLICITLINEEND(1, 4), ENDMARKER(2),]),
        ('"\'"', [STRING(1, 1, '"\'"'), IMPLICITLINEEND(1, 4), ENDMARKER(2),]),
        (
            # This is a weird one: "shrink" should be interpreted as an ID.
            '"doesn\'t "shrink", does it"',
            [
                STRING(1, 1, '"doesn\'t "'),
                NAME(1, 11, "shrink"),
                STRING(1, 17, '", does it"'),
                IMPLICITLINEEND(1, 28),
                ENDMARKER(2),
            ],
        ),
        ## Multi line.
        (
            dedent_multiline(
                """
                laser l1 (
                    # some comment
                    P=5
                )
                """
            ),
            [
                NAME(1, 1, "laser"),
                SPACE(1, 6),
                NAME(1, 7, "l1"),
                SPACE(1, 9),
                LPAREN(1, 10),
                NEWLINE(1, 11),
                SPACE(2, 1, 4),
                COMMENT(2, 5, "# some comment"),
                NEWLINE(2, 19),
                SPACE(3, 1, 4),
                NAME(3, 5, "P"),
                EQUALS(3, 6),
                NUMBER(3, 7, "5"),
                NEWLINE(3, 8),
                RPAREN(4, 1),
                IMPLICITLINEEND(4, 2),
                ENDMARKER(5),
            ],
        ),
    ),
)
def test_lines(tokenizer, string, expected):
    assert list(tokenizer.tokenize(string)) == expected
