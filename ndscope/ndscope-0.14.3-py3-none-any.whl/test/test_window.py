from ..__main__ import parse_window_str


WINDOW_TESTS = [
    ('[-10,0]', (-10, 0)),
    ('[-10,]', (-10, 0)),
    (',-10', (-10, 0)),
    ('0,-10', (-10, 0)),
    ('5,-5', (-5, 5)),
    ('-5.,5.3', (-5, 5.3)),
    ('[-3, 20]', (-3, 20)),
    ('(3.33, -6.343)', (-6.343, 3.33)),
    ('234.24', 234.24),
]


def test_window():
    for i, o in WINDOW_TESTS:
        oo = parse_window_str(i)
        assert oo == o
