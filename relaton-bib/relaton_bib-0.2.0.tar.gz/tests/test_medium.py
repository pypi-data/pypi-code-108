import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import Medium


@pytest.fixture
def subject():
    return Medium(form="form", size="size", scale="scale")


@pytest.fixture
def subject_none():
    return Medium()


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert host.find("./medium/form").text == "form"
    assert host.find("./medium/size").text == "size"
    assert result.find("./scale").text == "scale"


def test_to_xml_with_no_props(subject_none):
    host = ET.Element("host")
    result = subject_none.to_xml(host)

    assert result is not None
    assert host.find("./medium") is not None


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc("""medium.form:: form
                                         medium.size:: size
                                         medium.scale:: scale""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib("p")

    assert result == inspect.cleandoc("""p.medium.form:: form
                                         p.medium.size:: size
                                         p.medium.scale:: scale""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["form"] == "form"
    assert result["size"] == "size"
    assert result["scale"] == "scale"
