import pytest

import dataclasses
import logging

import xml.etree.ElementTree as ET

from relaton_bib import BibliographicItem, DocumentRelation


@pytest.fixture
def subject():
    return DocumentRelation(
        type=DocumentRelation.Type.partOf,
        bibitem=BibliographicItem())


def test_warn_when_type_invalid(caplog):
    invalid = "invalid"

    with caplog.at_level(logging.WARNING):
        DocumentRelation(type=invalid, bibitem=None)

    assert f"invalid relation type: {invalid}" in caplog.text


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert result.attrib["type"] == DocumentRelation.Type.partOf
    assert host.find("./relation/description") is None


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert "type:: partOf" in result


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="tt")

    assert "tt.type:: partOf" in result


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["type"] == DocumentRelation.Type.partOf
