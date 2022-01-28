import pytest
from finesse.script.legacy import KatParser


@pytest.fixture
def parser():
    return KatParser()
