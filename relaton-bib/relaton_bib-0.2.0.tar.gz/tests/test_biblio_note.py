import pytest
import inspect

import dataclasses
import xml.etree.ElementTree as ET

from relaton_bib import BiblioNote, BiblioNoteCollection


@pytest.fixture
def biblio_note():
    return BiblioNote(type="type", content="content")


@pytest.fixture
def bibnote_collection():
    return BiblioNoteCollection([
        BiblioNote(type="type1", content="content1", language=["en"]),
        BiblioNote(type="тип2", content="содержимое2", language=["ru"])])


def test_note_to_xml(biblio_note):
    host = ET.Element("host")
    result = biblio_note.to_xml(host)

    assert result.attrib["type"] == "type"
    assert host.find("./note").text == "content"


def test_note_to_asciibib(biblio_note):
    result = biblio_note.to_asciibib(prefix="test")

    assert result == inspect.cleandoc(
        """test.biblionote.type:: type
           test.biblionote.content:: content""")


def test_note_hash(biblio_note):
    result = dataclasses.asdict(biblio_note)

    assert result["type"] == "type"
    assert result["content"] == "content"


def test_note_collecion_to_xml(bibnote_collection):
    host = ET.Element("host")
    result = bibnote_collection.to_xml(host, {"lang": "en"})

    assert result is not None
    assert len(host.findall("./note")) == 1
    assert host.find("./note").text == "content1"
    assert host.find("./note").attrib["language"] == "en"


def test_note_collecion_to_xml_lang_not_found(bibnote_collection):
    host = ET.Element("host")
    result = bibnote_collection.to_xml(host, {"lang": "xx"})

    assert result is not None
    assert len(host.findall("./note")) == 2


def test_note_collecion_hash(bibnote_collection):
    result = dataclasses.asdict(bibnote_collection)

    assert result["array"][0]["type"] == "type1"
    assert result["array"][0]["content"] == "content1"
    assert result["array"][1] is not None
