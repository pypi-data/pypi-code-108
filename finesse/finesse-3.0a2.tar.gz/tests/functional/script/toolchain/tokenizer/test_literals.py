import pytest
from finesse.script.containers import KatToken
from ..util import IMPLICITLINEEND, ENDMARKER


@pytest.mark.parametrize(
    "token,string",
    (
        ("EQUALS", "="),
        ("PLUS", "+"),
        ("MINUS", "-"),
        ("POWER", "**"),
        ("TIMES", "*"),
        ("FLOORDIVIDE", "//"),
        ("DIVIDE", "/"),
        ("COMMA", ","),
        # FIXME: These throw exceptions because of unbalanced delimiters...
        # ("LBRACKET", "["),
        # ("RBRACKET", "]"),
        # ("LPAREN", "("),
        # ("RPAREN", ")"),
    ),
)
def test_literal(tokenizer, token, string):
    assert list(tokenizer.tokenize(string)) == [
        KatToken(1, 1, 1 + len(string), token, string),
        IMPLICITLINEEND(1, 1 + len(string)),
        ENDMARKER(2),
    ]
