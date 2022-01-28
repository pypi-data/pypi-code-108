import dataclasses
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import DocRelationCollection, DocumentRelation, \
    FormattedRef, BibliographicItem


@pytest.fixture
def subject():
    return DocRelationCollection([
        DocumentRelation(
            type=DocumentRelation.Type.replace,
            bibitem=BibliographicItem(
                formattedref=FormattedRef(content="realtion1"),
            )),
        DocumentRelation(
            type=DocumentRelation.Type.obsoletes,
            bibitem=BibliographicItem(
                formattedref=FormattedRef(content="realtion2"),
            ))])


def test_returns_one_replace(subject):
    assert len(subject) == 2
    assert len(subject.replaces()) == 1


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert len(result.findall("./relation")) == 2
    assert host.findall("./relation")[0].attrib["type"] \
        == DocumentRelation.Type.replace
    assert host.findall("./relation")[1].attrib["type"] \
        == DocumentRelation.Type.obsoletes


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert "relation::" in result


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="test")

    assert "test.relation::" in result


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["array"][0]["type"] == DocumentRelation.Type.replace
    assert result["array"][1]["type"] == DocumentRelation.Type.obsoletes
