import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import TypedTitleString, \
    TypedTitleStringCollection, FormattedString


def test_missing_title_or_content():
    with pytest.raises(ValueError) as excinfo:
        TypedTitleString(type="type")
    assert "Argument title or content should be passed" in str(excinfo.value)


@pytest.fixture
def subject():
    return TypedTitleString(
        type=TypedTitleString.Type.MAIN,
        title=FormattedString(content="Title", format=None)
    )


def test_valid_instance(subject):
    assert type(subject) is TypedTitleString


def test_to_xml(subject):
    host = ET.Element("host")
    subject.to_xml(host)

    assert host.attrib["type"] == TypedTitleString.Type.MAIN
    assert host.text == "Title"


def test_to_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["type"] == TypedTitleString.Type.MAIN
    assert result["title"]["content"] == "Title"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """title.type:: main
           title.content:: Title""")


def test_from_string_empty():
    t = TypedTitleString.from_string("")
    assert len(t) == 2
    assert t[0].title.content == ""
    assert t[0].type == TypedTitleString.Type.TMAIN
    assert t[1].title.content == ""
    assert t[1].type == TypedTitleString.Type.MAIN


def test_with_main():
    t = TypedTitleString.from_string("Main")
    assert len(t) == 2
    assert t[0].title.content == "Main"
    assert t[0].type == TypedTitleString.Type.TMAIN
    assert t[1].title.content == "Main"
    assert t[1].type == TypedTitleString.Type.MAIN


def test_with_main_and_part():
    t = TypedTitleString.from_string("Main - Part 1:")
    assert len(t) == 3
    assert t[0].title.content == "Main"
    assert t[0].type == TypedTitleString.Type.TMAIN
    assert t[1].title.content == "Part 1:"
    assert t[1].type == TypedTitleString.Type.TPART
    assert t[2].title.content == "Main - Part 1:"
    assert t[2].type == TypedTitleString.Type.MAIN


def test_with_intro_and_main():
    t = TypedTitleString.from_string("Intro - Main")
    assert len(t) == 3
    assert t[0].title.content == "Intro"
    assert t[0].type == TypedTitleString.Type.TINTRO
    assert t[1].title.content == "Main"
    assert t[1].type == TypedTitleString.Type.TMAIN
    assert t[2].title.content == "Intro - Main"
    assert t[2].type == TypedTitleString.Type.MAIN


def test_with_intro_and_main_and_part():
    t = TypedTitleString.from_string("Intro - Main - Part 1:")
    assert len(t) == 4
    assert t[0].title.content == "Intro"
    assert t[0].type == TypedTitleString.Type.TINTRO
    assert t[1].title.content == "Main"
    assert t[1].type == TypedTitleString.Type.TMAIN
    assert t[2].title.content == "Part 1:"
    assert t[2].type == TypedTitleString.Type.TPART
    assert t[3].title.content == "Intro - Main - Part 1:"
    assert t[3].type == TypedTitleString.Type.MAIN


def test_with_extra_part():
    t = TypedTitleString.from_string("Intro - Main - Part 1: - Extra")
    assert len(t) == 4
    assert t[0].title.content == "Intro"
    assert t[0].type == TypedTitleString.Type.TINTRO
    assert t[1].title.content == "Main"
    assert t[1].type == TypedTitleString.Type.TMAIN
    assert t[2].title.content == "Part 1: -- Extra"
    assert t[2].type == TypedTitleString.Type.TPART
    assert t[3].title.content == "Intro - Main - Part 1: -- Extra"
    assert t[3].type == TypedTitleString.Type.MAIN


def test_filter_collection(subject):
    c = TypedTitleStringCollection([])
    assert len(c) == 0
    c.append(subject)
    assert len(c) == 1
    r = TypedTitleStringCollection(filter(lambda t: t.type == "some", c))
    assert len(r) == 0
    r = TypedTitleStringCollection(
        filter(lambda t: t.type == TypedTitleString.Type.MAIN, c))
    assert len(r) == 1
