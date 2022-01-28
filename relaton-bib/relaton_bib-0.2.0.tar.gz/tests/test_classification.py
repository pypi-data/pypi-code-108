import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import Classification


@pytest.fixture
def subject():
    return Classification(type="type", value="value")


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert result.attrib["type"] == "type"
    assert host.find("./classification").text == "value"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc("""classification.type:: type
                                         classification.value:: value""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="test")

    assert result == inspect.cleandoc("""test.classification.type:: type
                                         test.classification.value:: value""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["type"] == "type"
    assert result["value"] == "value"
