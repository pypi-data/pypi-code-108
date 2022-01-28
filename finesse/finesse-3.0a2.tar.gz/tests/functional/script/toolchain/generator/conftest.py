import pytest
from finesse.script.generator import KatUnbuilder, KatUnfiller
from finesse.script.graph import KatGraph


@pytest.fixture
def unbuilder(spec):
    return KatUnbuilder(spec=spec)


@pytest.fixture
def unfiller():
    return KatUnfiller()


@pytest.fixture
def graph(spec):
    return KatGraph()
