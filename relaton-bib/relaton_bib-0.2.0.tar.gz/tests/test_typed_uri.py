import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import TypedUri


@pytest.fixture
def subject():
    return TypedUri(type="type", content="https://metanorma.com")


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert result.attrib["type"] == "type"
    assert host.find("./uri").text == "https://metanorma.com"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """link.type:: type
           link.content:: https://metanorma.com""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="pref")

    assert result == inspect.cleandoc(
        """pref.link.type:: type
           pref.link.content:: https://metanorma.com""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["type"] == "type"
    assert result["content"] == "https://metanorma.com"


def test_invalid_uri():
    with pytest.raises(ValueError) as excinfo:
        TypedUri(type="type", content=":some_malformed_uri//")
    assert "Invalid content" in str(excinfo.value)


def test_set_content():
    uri = TypedUri(type="src", content=None)
    uri.content = "http://example.com"
    assert uri.content == "http://example.com"
