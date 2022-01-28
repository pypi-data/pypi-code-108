import pytest
from ..util import COMMENT, IMPLICITLINEEND, ENDMARKER


@pytest.mark.parametrize(
    "string,expected",
    (
        (
            "# comment",
            [COMMENT(1, 1, "# comment"), IMPLICITLINEEND(1, 10), ENDMARKER(2),],
        ),
        (
            "### comment",
            [COMMENT(1, 1, "### comment"), IMPLICITLINEEND(1, 12), ENDMARKER(2),],
        ),
        (
            "### comment ###",
            [COMMENT(1, 1, "### comment ###"), IMPLICITLINEEND(1, 16), ENDMARKER(2),],
        ),
    ),
)
def test_comment(tokenizer, string, expected):
    assert list(tokenizer.tokenize(string)) == expected
