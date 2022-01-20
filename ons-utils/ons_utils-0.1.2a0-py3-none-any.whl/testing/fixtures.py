import pytest


@pytest.fixture
def all_in_output():
    """Checks that all values are in the output."""
    def _(output, values):
        return all([x in values for x in output])
    return _
