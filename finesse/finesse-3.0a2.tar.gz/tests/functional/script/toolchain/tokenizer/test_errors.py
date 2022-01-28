"""Tests for the tokenizer without any normalization."""

import pytest
from finesse.script.exceptions import KatScriptError
from .....util import escape_full


@pytest.mark.parametrize(
    "string,error",
    (
        ("[", ("\nline 1: unclosed '['\n" "-->1: [\n" "      ^")),
        ("(", ("\nline 1: unclosed '('\n" "-->1: (\n" "      ^")),
        ("]", ("\nline 1: extraneous ']'\n" "-->1: ]\n" "      ^")),
        (")", ("\nline 1: extraneous ')'\n" "-->1: )\n" "      ^")),
    ),
)
def test_invalid_delimiter_nesting(tokenizer, string, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        list(tokenizer.tokenize(string))
