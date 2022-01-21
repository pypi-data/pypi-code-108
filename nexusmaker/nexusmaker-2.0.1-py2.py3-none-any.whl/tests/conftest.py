from pathlib import Path

import pytest
from nexusmaker import Record
from nexusmaker import NexusMaker
from nexusmaker import NexusMakerAscertained
from nexusmaker import NexusMakerAscertainedParameters


@pytest.fixture
def test_dir():
    return Path(__file__).parent

    
@pytest.fixture(scope='class')
def testdata():
    return [
        Record(Language="A", Parameter="eye", Item="", Cognacy="1"),
        Record(Language="A", Parameter="leg", Item="", Cognacy="1"),
        Record(Language="A", Parameter="arm", Item="", Cognacy="1"),

        Record(Language="B", Parameter="eye", Item="", Cognacy="1"),
        Record(Language="B", Parameter="leg", Item="", Cognacy="2"),
        Record(Language="B", Parameter="arm", Item="", Cognacy="2"),

        Record(Language="C", Parameter="eye", Item="", Cognacy="1"),
        # No Record for C 'leg'
        Record(Language="C", Parameter="arm", Item="", Cognacy="3"),

        Record(Language="D", Parameter="eye", Item="", Cognacy="1", Loan=True),
        Record(Language="D", Parameter="leg", Item="", Cognacy="1"),
        Record(Language="D", Parameter="leg", Item="", Cognacy="2"),
        Record(Language="D", Parameter="arm", Item="", Cognacy="2,3"),
    ]


@pytest.fixture(scope='class')
def nexusmaker(testdata):
    return NexusMaker(data=testdata)


@pytest.fixture(scope='class')
def nexusmakerasc(testdata):
    return NexusMakerAscertained(data=testdata)


@pytest.fixture(scope='class')
def nexusmakerascparameters(testdata):
    return NexusMakerAscertainedParameters(data=testdata)
