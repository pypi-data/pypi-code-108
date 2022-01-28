import pytest
from finesse.script.containers import TokenContainer, KatCoordinate, KatBounds, KatFile
from ..util import NEWLINE, NAME, SPACE


def bounds(a, b):
    return KatBounds(KatCoordinate(*a), KatCoordinate(*b))


class FakeTokenContainer(TokenContainer):
    def __init__(self, tokens):
        super().__init__()
        self._tokens = tokens

    @property
    def tokens(self):
        return self._tokens


@pytest.mark.parametrize(
    "tokens,bounds,expected",
    (
        # Substrings on same line.
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 1), (1, 6)), "test "),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 1), (1, 5)), "test"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 1), (1, 4)), "tes"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 1), (1, 3)), "te"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 1), (1, 2)), "t"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 1), (1, 1)), ""),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 2), (1, 2)), ""),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 2), (1, 3)), "e"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 2), (1, 4)), "es"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 2), (1, 5)), "est"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 2), (1, 6)), "est "),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 3), (1, 6)), "st "),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 3), (1, 5)), "st"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 3), (1, 4)), "s"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 3), (1, 3)), ""),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 4), (1, 4)), ""),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 4), (1, 5)), "t"),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 4), (1, 6)), "t "),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 5), (1, 6)), " "),
        ([NAME(1, 1, "test"), SPACE(1, 5)], bounds((1, 6), (1, 6)), ""),
        # Substrings across lines.
        (
            [
                NAME(1, 1, "test"),
                SPACE(1, 5),
                NEWLINE(1, 6),
                NAME(2, 1, "test"),
                SPACE(2, 5),
            ],
            bounds((1, 1), (2, 1)),
            "test \n",
        ),
        (
            [
                NAME(1, 1, "test"),
                SPACE(1, 5),
                NEWLINE(1, 6),
                NAME(2, 1, "test"),
                SPACE(2, 5),
            ],
            bounds((1, 1), (2, 2)),
            "test \nt",
        ),
        (
            [
                NAME(1, 1, "test"),
                SPACE(1, 5),
                NEWLINE(1, 6),
                NAME(2, 1, "test"),
                SPACE(2, 5),
            ],
            bounds((1, 1), (2, 5)),
            "test \ntest",
        ),
        (
            [
                NAME(1, 1, "test"),
                SPACE(1, 5),
                NEWLINE(1, 6),
                NAME(2, 1, "test"),
                SPACE(2, 5),
            ],
            bounds((1, 1), (2, 6)),
            "test \ntest ",
        ),
        (
            [
                NAME(1, 1, "test"),
                SPACE(1, 5),
                NEWLINE(1, 6),
                NEWLINE(2, 1),
                NAME(3, 1, "test"),
                SPACE(3, 5),
            ],
            bounds((1, 1), (3, 6)),
            "test \n\ntest ",
        ),
        # Whitespace.
        (
            [SPACE(1, 1, 4), NAME(1, 5, "test"), SPACE(1, 9)],
            bounds((1, 1), (1, 5)),
            "    ",
        ),
        (
            [SPACE(1, 1, 4), NAME(1, 5, "test"), SPACE(1, 9)],
            bounds((1, 1), (1, 6)),
            "    t",
        ),
        # Newlines.
        ([NEWLINE(1, 1), NEWLINE(2, 1)], bounds((1, 1), (2, 1)), "\n"),
        ([NEWLINE(1, 1), NEWLINE(2, 1)], bounds((1, 1), (2, 2)), "\n\n"),
    ),
)
def test_token_script(tokens, bounds, expected):
    container = FakeTokenContainer(tokens)
    assert container.script(bounds) == expected


@pytest.mark.parametrize(
    "script,bounds,expected",
    (
        # Substrings on same line.
        ("test ", bounds((1, 1), (1, 6)), "test "),
        ("test ", bounds((1, 1), (1, 5)), "test"),
        ("test ", bounds((1, 1), (1, 4)), "tes"),
        ("test ", bounds((1, 1), (1, 3)), "te"),
        ("test ", bounds((1, 1), (1, 2)), "t"),
        ("test ", bounds((1, 1), (1, 1)), ""),
        ("test ", bounds((1, 2), (1, 2)), ""),
        ("test ", bounds((1, 2), (1, 3)), "e"),
        ("test ", bounds((1, 2), (1, 4)), "es"),
        ("test ", bounds((1, 2), (1, 5)), "est"),
        ("test ", bounds((1, 2), (1, 6)), "est "),
        ("test ", bounds((1, 3), (1, 6)), "st "),
        ("test ", bounds((1, 3), (1, 5)), "st"),
        ("test ", bounds((1, 3), (1, 4)), "s"),
        ("test ", bounds((1, 3), (1, 3)), ""),
        ("test ", bounds((1, 4), (1, 4)), ""),
        ("test ", bounds((1, 4), (1, 5)), "t"),
        ("test ", bounds((1, 4), (1, 6)), "t "),
        ("test ", bounds((1, 5), (1, 6)), " "),
        ("test ", bounds((1, 6), (1, 6)), ""),
        # Substrings across lines.
        ("test \ntest ", bounds((1, 1), (2, 1)), "test \n"),
        ("test \ntest ", bounds((1, 1), (2, 2)), "test \nt"),
        ("test \ntest ", bounds((1, 1), (2, 5)), "test \ntest"),
        ("test \ntest ", bounds((1, 1), (2, 6)), "test \ntest "),
        ("test \n\ntest ", bounds((1, 1), (3, 6)), "test \n\ntest "),
        # Whitespace.
        ("    test ", bounds((1, 1), (1, 5)), "    "),
        ("    test ", bounds((1, 1), (1, 6)), "    t"),
        # Newlines.
        ("\n\n", bounds((1, 1), (2, 1)), "\n"),
        ("\n\n", bounds((1, 1), (2, 2)), "\n\n"),
        ("\n\n", bounds((1, 1), (3, 1)), "\n\n"),
    ),
)
def test_file_script(script, bounds, expected):
    container = KatFile(script)
    assert container.script(bounds) == expected


@pytest.mark.parametrize(
    "script,expected",
    (
        ("", bounds((1, 1), (1, 1))),
        ("t", bounds((1, 1), (1, 2))),
        ("te", bounds((1, 1), (1, 3))),
        ("tes", bounds((1, 1), (1, 4))),
        ("test", bounds((1, 1), (1, 5))),
        ("test ", bounds((1, 1), (1, 6))),
        # Multi-line.
        ("test \n", bounds((1, 1), (2, 1))),
        ("test \n\n", bounds((1, 1), (3, 1))),
        ("test \ntest\n", bounds((1, 1), (3, 1))),
    ),
)
def test_file_bounds(script, expected):
    container = KatFile(script)
    assert container.bounds == expected
