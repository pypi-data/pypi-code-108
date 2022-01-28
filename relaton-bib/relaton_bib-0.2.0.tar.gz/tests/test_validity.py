import dataclasses
import datetime
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import Validity


@pytest.fixture
def subject():
    return Validity(
        begins=datetime.datetime(2009, 1, 1, 0, 0),
        ends=datetime.datetime(2012, 11, 28, 1, 2))


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert host.find("./validity") == result
    assert result.find("./validityBegins").text == "2009-01-01 00:00"
    assert result.find("./validityEnds").text == "2012-11-28 01:02"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """validity.begins:: 2009-01-01 00:00
           validity.ends:: 2012-11-28 01:02""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="eee")

    assert result == inspect.cleandoc(
        """eee.validity.begins:: 2009-01-01 00:00
           eee.validity.ends:: 2012-11-28 01:02""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert type(result["begins"]) is datetime.datetime
    assert type(result["ends"]) is datetime.datetime
