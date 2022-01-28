import pytest

import dataclasses
import inspect
import logging
import xml.etree.ElementTree as ET

from relaton_bib import Series, TypedTitleString
from relaton_bib import FormattedRef
from relaton_bib import LocalizedString


@pytest.fixture
def subject_min():
    return Series(type="main", title=TypedTitleString(content="value"))


def test_invalid_type(caplog):
    invalid = "invalid"

    with caplog.at_level(logging.WARNING):
        Series(type=invalid, title=TypedTitleString(content="value"))

    assert f"[relaton-bib] Series type is invalid: {invalid}" in caplog.text


def test_missing_title_and_formattedref():
    with pytest.raises(ValueError) as excinfo:
        Series(type="alt")
    assert "arg `title` or `formattedref` should present" in str(excinfo.value)


def test_to_xml(subject_min):
    host = ET.Element("host")
    result = subject_min.to_xml(host)

    assert host.find("./series") is not None
    assert result.attrib["type"] == "main"
    assert result.find("./title").text == "value"
    assert result.find("./title").attrib["format"] == "text/plain"


def test_to_asciibib(subject_min):
    result = subject_min.to_asciibib()

    assert result == inspect.cleandoc(
        """series.type:: main
           series.title.content:: value
           series.title.format:: text/plain""")


def test_to_asciibib_with_pref(subject_min):
    result = subject_min.to_asciibib(prefix="test")

    assert result == inspect.cleandoc(
        """test.series.type:: main
           test.series.title.content:: value
           test.series.title.format:: text/plain""")


def test_hash(subject_min):
    result = dataclasses.asdict(subject_min)

    assert result["type"] == "main"


@pytest.fixture
def subject_full():
    return Series(
        type="main",
        formattedref=FormattedRef("abbrv", "en", "Latn"),
        place="some_place",
        organization="org",
        abbreviation=LocalizedString("abbrv", "en", "Latn"),
        from_="from",
        to="to",
        number="123",
        partnumber="321")


def test_full_to_xml(subject_full):
    host = ET.Element("host")
    result = subject_full.to_xml(host)

    assert host.find("./series") is not None
    assert result.attrib["type"] == "main"
    assert result.find("./title") is None


def test_full_to_asciibib(subject_full):
    result = subject_full.to_asciibib()

    assert result == inspect.cleandoc(
        """series.type:: main
           series.formattedref.content:: abbrv
           series.formattedref.language:: en
           series.formattedref.script:: Latn
           series.formattedref.format:: text/plain
           series.place:: some_place
           series.organization:: org
           series.abbreviation.content:: abbrv
           series.abbreviation.language:: en
           series.abbreviation.script:: Latn
           series.from:: from
           series.to:: to
           series.number:: 123
           series.partnumber:: 321""")


def test_full_to_asciibib_with_pref(subject_full):
    result = subject_full.to_asciibib(prefix="pref")

    assert result == inspect.cleandoc(
        """pref.series.type:: main
           pref.series.formattedref.content:: abbrv
           pref.series.formattedref.language:: en
           pref.series.formattedref.script:: Latn
           pref.series.formattedref.format:: text/plain
           pref.series.place:: some_place
           pref.series.organization:: org
           pref.series.abbreviation.content:: abbrv
           pref.series.abbreviation.language:: en
           pref.series.abbreviation.script:: Latn
           pref.series.from:: from
           pref.series.to:: to
           pref.series.number:: 123
           pref.series.partnumber:: 321""")


def test_full_hash(subject_full):
    result = dataclasses.asdict(subject_full)

    assert result["type"] == "main"
    assert result["place"] == "some_place"
    assert result["from_"] == "from"
    assert result["to"] == "to"
    assert result["number"] == "123"
    assert result["partnumber"] == "321"
