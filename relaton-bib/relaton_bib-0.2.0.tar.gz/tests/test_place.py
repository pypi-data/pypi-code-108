import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import Place


@pytest.fixture
def subject():
    return Place(name="name", region="FR")


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert result.attrib["region"] == "FR"
    assert host.find("./place").text == "name"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc("""place.name:: name
                                         place.region:: FR""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib("m")

    assert result == inspect.cleandoc("""m.place.name:: name
                                         m.place.region:: FR""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["name"] == "name"
    assert result["region"] == "FR"
