from dynamo_io.mock import _expressions

from pytest import mark

SCENARIOS = [
    ("SET foo, bar, baz REMOVE a, b, c", "SET", "foo, bar, baz"),
    ("SET foo, bar, baz REMOVE a, b, c", "REMOVE", "a, b, c"),
    ("SET foo, bar, baz", "REMOVE", None),
    ("SET foo, bar, baz REMOVE", "REMOVE", None),
]


@mark.parametrize("expression, keyword, expected", SCENARIOS)
def test_get_clause(expression: str, keyword: str, expected: str):
    """Should extract the expected clause for the scenario."""
    assert expected == _expressions.get_clause(keyword, expression)
