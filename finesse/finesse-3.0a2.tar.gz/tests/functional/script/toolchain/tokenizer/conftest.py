import pytest
from finesse.script.tokenizer import KatTokenizer


@pytest.fixture
def tokenizer():
    return KatTokenizer()
