import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import WorkGroup


@pytest.fixture
def subj_min():
    return WorkGroup(name="value")


@pytest.fixture
def subj_full():
    return WorkGroup(name="value",
                     number=1,
                     type="type")


def test_min_to_xml(subj_min):
    host = ET.Element("host")
    result = subj_min.to_xml(host)

    assert result.text == "value"


def test_full_to_xml(subj_full):
    host = ET.Element("host")
    result = subj_full.to_xml(host)

    assert result.text == "value"
    assert result.attrib["type"] == "type"
    assert result.attrib["number"] == "1"


def test_min_to_asciibib(subj_min):
    result = subj_min.to_asciibib()

    assert result == "name:: value"


def test_full_to_asciibib(subj_full):
    result = subj_full.to_asciibib()

    assert result == inspect.cleandoc(
        """name:: value
           number:: 1
           type:: type""")


def test_min_to_asciibib_with_pref(subj_min):
    result = subj_min.to_asciibib(prefix="test")

    assert result == "test.name:: value"


def test_full_to_asciibib_with_pref(subj_full):
    result = subj_full.to_asciibib(prefix="test")

    assert result == inspect.cleandoc(
        """test.name:: value
           test.number:: 1
           test.type:: type""")


def test_hash(subj_full):
    result = dataclasses.asdict(subj_full)

    assert result["type"] == "type"
    assert result["number"] == 1
    assert result["name"] == "value"
