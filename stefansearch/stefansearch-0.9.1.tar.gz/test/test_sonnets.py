import pytest
from stefansearch.engine.search_engine import SearchEngine
from stefansearch.scoring.ql import QlScorer
from stefansearch.scoring.bm25 import Bm25Scorer
from stefansearch.tokenizing.alphanumeric_tokenizer import AlphanumericTokenizer
from util import create_engine, TESTDATA_PATH
"""
Very simple test cases for the sonnets.

Note: these test cases have the problem that they are always the first line
of the sonnet. This is okay for now but should be fixed when I put a little 
more effort in!
"""
# TODO: TEST THAT ABBREVIATIONS CAN STILL BE FOUND CORRECTLY


# Use scope='session' to reuse without re-generating
@pytest.fixture(scope='session')
def sonnets_engine() -> SearchEngine:
    """Creates a search engine with all of Shakespeare's sonnets indexed."""
    engine = create_engine(tokenizer=AlphanumericTokenizer())
    # Index all sonnets
    sonnets_dir = TESTDATA_PATH / 'Sonnets'
    for sonnet_path in sonnets_dir.glob('*'):
        sonnet_num = int(sonnet_path.stem)
        engine.index_file(sonnet_path, make_slug(sonnet_num))
    return engine


def make_slug(sonnet_number: int) -> str:
    return 'SONNET-{}'.format(sonnet_number)


# Start QL tests
def test_query_1(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("Weary with toil, I haste me to my bed")
    assert res[0].slug == make_slug(27)
    assert res[0].score == -21.520006033459808


def test_query_2(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("Let me not to the marriage of true minds")
    assert res[0].slug == make_slug(116)
    assert res[0].score == -20.5673062109939


def test_query_3(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("My mistress' eyes are nothing like the sun")
    assert res[0].slug == make_slug(130)
    assert res[0].score == -20.092107486147174


def test_query_4(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("The expense of spirit in a waste of shame")
    assert res[0].slug == make_slug(129)
    assert res[0].score == -19.777450503219303


def test_query_5(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("When in the chronicle of wasted time")
    assert res[0].slug == make_slug(106)
    assert res[0].score == -16.325642535181206


def test_query_6(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("Shall I compare thee to a summer’s day?")
    assert res[0].slug == make_slug(18)
    assert res[0].score == -20.504173217961355


def test_query_7(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("So now I have confessed that he is thine")
    assert res[0].slug == make_slug(134)
    assert res[0].score == -20.979012760089027


def test_query_8(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("To me, fair friend, you never can be old")
    assert res[0].slug == make_slug(104)
    assert res[0].score == -22.103154435395787


def test_query_9(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("When in disgrace with fortune and men’s eyes")
    assert res[0].slug == make_slug(29)
    assert res[0].score == -21.72004365822967


def test_query_10(sonnets_engine):
    sonnets_engine._scorer = QlScorer()
    res = sonnets_engine.search("From you have I been absent in the spring")
    assert res[0].slug == make_slug(98)
    assert res[0].score == -21.559573753181454


# Start BM25 Tests
def test_query_11(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("Weary with toil, I haste me to my bed")
    assert res[0].slug == make_slug(27)
    assert res[0].score == 3.3942308383190047


def test_query_12(sonnets_engine):
    # TODO: BM25 GIVES US A BAD ANSWER
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("Let me not to the marriage of true minds")
    assert res[0].slug == make_slug(36)
    assert res[0].score == 0.7825224158987157


def test_query_13(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("My mistress' eyes are nothing like the sun")
    assert res[0].slug == make_slug(130)
    assert res[0].score == 5.757886923342326


def test_query_14(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("The expense of spirit in a waste of shame")
    assert res[0].slug == make_slug(129)
    assert res[0].score == 1.3046924580067916


def test_query_15(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("When in the chronicle of wasted time")
    assert res[0].slug == make_slug(106)
    assert res[0].score == 1.69059291600607


def test_query_16(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("Shall I compare thee to a summer’s day?")
    assert res[0].slug == make_slug(18)
    assert res[0].score == 2.2399816041141682


def test_query_17(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("So now I have confessed that he is thine")
    assert res[0].slug == make_slug(134)
    assert res[0].score == 3.0794881617749135


def test_query_18(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("To me, fair friend, you never can be old")
    assert res[0].slug == make_slug(104)
    assert res[0].score == 4.94198548680906


def test_query_19(sonnets_engine):
    # TODO: THIS GIVES US A PRETTY BAD ANSWER (BM25)
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("When in disgrace with fortune and men’s eyes")
    assert res[0].slug == make_slug(32)  #make_slug(29)
    assert res[0].score == 0.8685964709272731


def test_query_20(sonnets_engine):
    sonnets_engine._scorer = Bm25Scorer()
    res = sonnets_engine.search("From you have I been absent in the spring")
    assert res[0].slug == make_slug(98)
    assert res[0].score == 2.9521473910601936
