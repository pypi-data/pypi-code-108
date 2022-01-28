import pytest
from finesse.script.exceptions import KatScriptError
from ..data import STRINGS
from ..util import IMPLICITLINEEND, ENDMARKER, STRING


@pytest.mark.parametrize("string,_a,_b", STRINGS)
def test_strings(tokenizer, string, _a, _b):
    assert list(tokenizer.tokenize(string)) == [
        STRING(1, 1, string),
        IMPLICITLINEEND(1, 1 + len(string)),
        ENDMARKER(2),
    ]


@pytest.mark.parametrize(
    "string",
    (
        '"my \nstring"',
        '"my \n\rstring"',
        '"my \r\nstring"',
        '"\n\nmy\r\n\r \n \r \r\nstr\n\ring\n\r"',
    ),
)
def test_strings_cannot_have_newlines(tokenizer, string):
    """Test that strings cannot contain newline characters."""
    with pytest.raises(KatScriptError, match=r"\""):
        list(tokenizer.tokenize(string))
