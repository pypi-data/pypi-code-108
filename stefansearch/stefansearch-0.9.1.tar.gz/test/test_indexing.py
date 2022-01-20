import pytest
from stefansearch.engine.search_engine import SearchEngine
from stefansearch.tokenizing.alphanumeric_tokenizer import AlphanumericTokenizer
from util import create_engine
"""Very simple test cases for internal SearchEngine state."""


@pytest.fixture
def test_engine() -> SearchEngine:
    return create_engine(tokenizer=AlphanumericTokenizer())


# TODO: maybe a "SimulatedDocument" dataclass?
DOCUMENT_1 = 'APPLE BANANA CARROT DRAGONFRUIT EGGPLANT FIG'
DOCUMENT_2 = 'AIRPLANE BALL CACTUS DOVE EAR FISH GOAT HAMBURGER ICECREAM JUICE'
DOCUMENT_3 = 'APPLE CARROT CACTUS'


def test_init(test_engine):
    assert test_engine.num_docs == 0
    assert test_engine.num_terms == 0


def test_add(test_engine):
    test_engine.index_string(DOCUMENT_1, '1')
    assert test_engine.num_docs == 1
    assert test_engine.num_terms == 6
    test_engine.index_string(DOCUMENT_2, '2')
    assert test_engine.num_docs == 2
    assert test_engine.num_terms == 16
    test_engine.index_string(DOCUMENT_3, '3')
    assert test_engine.num_docs == 3
    assert test_engine.num_terms == 19


def test_remove(test_engine):
    test_engine.index_string(DOCUMENT_1, '1')
    test_engine.index_string(DOCUMENT_2, '2')
    test_engine.index_string(DOCUMENT_3, '3')
    test_engine.remove_document('1')
    assert test_engine.num_docs == 2
    assert test_engine.num_terms == 13
    test_engine.remove_document('3')
    assert test_engine.num_docs == 1
    assert test_engine.num_terms == 10
    test_engine.remove_document('2')
    assert test_engine.num_docs == 0
    assert test_engine.num_terms == 0
