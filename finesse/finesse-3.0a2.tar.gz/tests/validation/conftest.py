import pytest
from finesse import Model


@pytest.fixture
def model():
    return Model()
