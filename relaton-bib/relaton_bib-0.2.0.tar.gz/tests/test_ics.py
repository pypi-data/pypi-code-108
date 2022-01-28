import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import ICS


@pytest.fixture
def subject():
    return ICS(code="code", text="text")


def test_to_xml(subject):
    host = ET.Element("host")
    subject.to_xml(host)

    assert host.find("./ics/code").text == "code"
    assert host.find("./ics/text").text == "text"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc("""ics.code:: code
                                         ics.text:: text""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib("p")

    assert result == inspect.cleandoc("""p.ics.code:: code
                                         p.ics.text:: text""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["code"] == "code"
    assert result["text"] == "text"
