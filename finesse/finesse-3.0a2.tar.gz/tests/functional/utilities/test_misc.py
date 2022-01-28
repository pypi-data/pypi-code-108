"""Misc utility unit tests."""

from hypothesis import given
from hypothesis.strategies import from_regex
from finesse.utilities.misc import check_name


@given(name=from_regex("^[a-zA-Z_][a-zA-Z0-9_]*$", fullmatch=True))
def test_check_name(name):
    """Test that check name is valid for various inputs."""
    check_name(name)
