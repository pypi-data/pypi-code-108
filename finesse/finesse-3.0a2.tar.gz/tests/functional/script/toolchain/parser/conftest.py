import pytest
from finesse.script.parser import KatParser


@pytest.fixture
def parser():
    return KatParser()
