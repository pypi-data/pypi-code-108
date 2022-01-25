from pathlib import Path

import pytest


@pytest.fixture
def here():
    return Path(__file__).parent
