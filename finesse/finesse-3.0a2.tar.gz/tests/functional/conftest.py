import pytest
from finesse.model import Model


@pytest.fixture
def model():
    return Model()
