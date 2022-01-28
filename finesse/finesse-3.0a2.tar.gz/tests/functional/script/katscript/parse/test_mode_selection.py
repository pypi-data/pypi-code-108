"""Kat file parser mode selection syntax tests."""

import pytest
from finesse.script import parse
from finesse.script.exceptions import KatScriptError
from .....util import escape_full


@pytest.mark.parametrize(
    "modes,expected",
    (
        # Keywords.
        ("even, 4", [[0, 0], [0, 2], [0, 4], [2, 0], [2, 2], [4, 0]]),
        ("odd, 3", [[0, 0], [0, 1], [0, 3], [1, 0], [1, 1], [3, 0]]),
        ("x, 5", [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]),
        ("y, 4", [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]),
        # Arrays.
        ("[[0, 0], [1, 1], [2, 2]]", [[0, 0], [1, 1], [2, 2]]),
    ),
)
def test_modes(modes, expected):
    model = parse(f"modes({modes})")
    assert expected in model.homs


# NOTE: these errors should ideally mark only the relevant parameters, not the full
# line; see #246.
@pytest.mark.parametrize(
    "modes,error",
    (
        pytest.param(
            "[3, 2]",
            "\nline 1: Expected mode list to be a two-dimensional list\n"
            "-->1: modes([3, 2])\n"
            "      ^^^^^^^^^^^^^",
            id="[3, 2]",
        ),
        pytest.param(
            "[[[0, 1], [1, 0]], [1, 2], [3, 4], [5, 6]]",
            "\nline 1: Expected n (= [0, 1]) and m (= [1, 0]) of element [[0, 1], [1, 0]] of mode "
            "list to be convertible to non-negative integers.\n"
            "-->1: modes([[[0, 1], [1, 0]], [1, 2], [3, 4], [5, 6]])\n"
            "      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
            "Syntax: modes(modes=none, maxtem=none, include=none, remove=none)",
            id=">2D nested list",
        ),
        pytest.param(
            "maxtem=-1",
            "\nline 1: Argument maxtem must be a non-negative integer.\n"
            "-->1: modes(maxtem=-1)\n"
            "      ^^^^^^^^^^^^^^^^",
            id="negative integer",
        ),
        pytest.param(
            "maxtem=3.141",
            "\nline 1: Argument maxtem must be a non-negative integer.\n"
            "-->1: modes(maxtem=3.141)\n"
            "      ^^^^^^^^^^^^^^^^^^^",
            id="non integer",
        ),
    ),
)
def test_invalid_modes(modes, error):
    with pytest.raises(KatScriptError, match=escape_full(error)):
        parse(f"modes({modes})")
