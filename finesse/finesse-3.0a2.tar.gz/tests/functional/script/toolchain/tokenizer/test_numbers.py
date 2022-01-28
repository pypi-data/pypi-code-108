import pytest
from ..data import SI_PREFICES, INTEGERS, FLOATS, FLOATS_STD, IMAGINARIES
from ..util import (
    NAME,
    NUMBER,
    MINUS,
    LPAREN,
    RPAREN,
    EQUALS,
    SPACE,
    IMPLICITLINEEND,
    ENDMARKER,
)


@pytest.mark.parametrize(
    "string,expected",
    (
        ("0", [NUMBER(1, 1, "0"), IMPLICITLINEEND(1, 2), ENDMARKER(2)]),
        ("1", [NUMBER(1, 1, "1"), IMPLICITLINEEND(1, 2), ENDMARKER(2)]),
        ("10", [NUMBER(1, 1, "10"), IMPLICITLINEEND(1, 3), ENDMARKER(2)]),
        ("100", [NUMBER(1, 1, "100"), IMPLICITLINEEND(1, 4), ENDMARKER(2)]),
        ("12345", [NUMBER(1, 1, "12345"), IMPLICITLINEEND(1, 6), ENDMARKER(2)]),
        (
            "(-124561-1)",
            [
                LPAREN(1, 1),
                MINUS(1, 2),
                NUMBER(1, 3, "124561"),
                MINUS(1, 9),
                NUMBER(1, 10, "1"),
                RPAREN(1, 11),
                IMPLICITLINEEND(1, 12),
                ENDMARKER(2),
            ],
        ),
        # Long integer.
        (
            "a = 123141242151251616110",
            [
                NAME(1, 1, "a"),
                SPACE(1, 2),
                EQUALS(1, 3),
                SPACE(1, 4),
                NUMBER(1, 5, "123141242151251616110"),
                IMPLICITLINEEND(1, 26),
                ENDMARKER(2),
            ],
        ),
        # Separation using `_`.
        ("1_000", [NUMBER(1, 1, "1_000"), IMPLICITLINEEND(1, 6), ENDMARKER(2)]),
        ("1_0_00", [NUMBER(1, 1, "1_0_00"), IMPLICITLINEEND(1, 7), ENDMARKER(2)]),
        ("1_0_0_0", [NUMBER(1, 1, "1_0_0_0"), IMPLICITLINEEND(1, 8), ENDMARKER(2)]),
        ("1000_000", [NUMBER(1, 1, "1000_000"), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        (
            "1_000_000",
            [NUMBER(1, 1, "1_000_000"), IMPLICITLINEEND(1, 10), ENDMARKER(2)],
        ),
    ),
)
def test_int(tokenizer, string, expected):
    assert list(tokenizer.tokenize(string)) == expected


@pytest.mark.parametrize(
    "string,expected",
    (
        ("3.14159", [NUMBER(1, 1, "3.14159"), IMPLICITLINEEND(1, 8), ENDMARKER(2)]),
        ("314159.", [NUMBER(1, 1, "314159."), IMPLICITLINEEND(1, 8), ENDMARKER(2)]),
        (".314159", [NUMBER(1, 1, ".314159"), IMPLICITLINEEND(1, 8), ENDMARKER(2)]),
        ("3e14159", [NUMBER(1, 1, "3e14159"), IMPLICITLINEEND(1, 8), ENDMARKER(2)]),
        ("3E123", [NUMBER(1, 1, "3E123"), IMPLICITLINEEND(1, 6), ENDMARKER(2)]),
        ("3e-1230", [NUMBER(1, 1, "3e-1230"), IMPLICITLINEEND(1, 8), ENDMARKER(2)]),
        ("3.14e159", [NUMBER(1, 1, "3.14e159"), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        ("0.0", [NUMBER(1, 1, "0.0"), IMPLICITLINEEND(1, 4), ENDMARKER(2)]),
        ("0.00", [NUMBER(1, 1, "0.00"), IMPLICITLINEEND(1, 5), ENDMARKER(2)]),
        ("0.000", [NUMBER(1, 1, "0.000"), IMPLICITLINEEND(1, 6), ENDMARKER(2)]),
        ("1.0", [NUMBER(1, 1, "1.0"), IMPLICITLINEEND(1, 4), ENDMARKER(2)]),
        ("2.00", [NUMBER(1, 1, "2.00"), IMPLICITLINEEND(1, 5), ENDMARKER(2)]),
        ("3.000", [NUMBER(1, 1, "3.000"), IMPLICITLINEEND(1, 6), ENDMARKER(2)]),
        # Separation using `_`.
        ("1_000.", [NUMBER(1, 1, "1_000."), IMPLICITLINEEND(1, 7), ENDMARKER(2)]),
        ("1_0_00.", [NUMBER(1, 1, "1_0_00."), IMPLICITLINEEND(1, 8), ENDMARKER(2)]),
        ("1_0_0_0.", [NUMBER(1, 1, "1_0_0_0."), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        (
            "1000_000.",
            [NUMBER(1, 1, "1000_000."), IMPLICITLINEEND(1, 10), ENDMARKER(2)],
        ),
        (
            "1_000_000.",
            [NUMBER(1, 1, "1_000_000."), IMPLICITLINEEND(1, 11), ENDMARKER(2)],
        ),
        (
            "1_234.5_678",
            [NUMBER(1, 1, "1_234.5_678"), IMPLICITLINEEND(1, 12), ENDMARKER(2)],
        ),
    ),
)
def test_float(tokenizer, string, expected):
    assert list(tokenizer.tokenize(string)) == expected


@pytest.mark.parametrize(
    "string,expected",
    (
        ("3.14159j", [NUMBER(1, 1, "3.14159j"), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        ("314159.j", [NUMBER(1, 1, "314159.j"), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        (".314159j", [NUMBER(1, 1, ".314159j"), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        ("3e14159j", [NUMBER(1, 1, "3e14159j"), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        ("3E123j", [NUMBER(1, 1, "3E123j"), IMPLICITLINEEND(1, 7), ENDMARKER(2)]),
        ("3e-1230j", [NUMBER(1, 1, "3e-1230j"), IMPLICITLINEEND(1, 9), ENDMARKER(2)]),
        (
            "3.14e159j",
            [NUMBER(1, 1, "3.14e159j"), IMPLICITLINEEND(1, 10), ENDMARKER(2)],
        ),
        # Separation using `_`.
        ("1_000j", [NUMBER(1, 1, "1_000j"), IMPLICITLINEEND(1, 7), ENDMARKER(2)]),
    ),
)
def test_imaginary(tokenizer, string, expected):
    assert list(tokenizer.tokenize(string)) == expected


@pytest.mark.parametrize("number,_a,_b", INTEGERS + FLOATS + IMAGINARIES)
def test_numbers(tokenizer, number, _a, _b):
    assert list(tokenizer.tokenize(number)) == [
        NUMBER(1, 1, number),
        IMPLICITLINEEND(1, 1 + len(str(number))),
        ENDMARKER(2),
    ]


@pytest.mark.parametrize("number,_a,_b", INTEGERS + FLOATS_STD)
@pytest.mark.parametrize("prefix,exponent", SI_PREFICES.items())
def test_numbers_with_si_prefices(tokenizer, number, _a, _b, prefix, exponent):
    string = f"{number}{prefix}"
    assert list(tokenizer.tokenize(string)) == [
        NUMBER(1, 1, string),
        IMPLICITLINEEND(1, 1 + len(str(string))),
        ENDMARKER(2),
    ]
