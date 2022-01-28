import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import DocumentIdentifier, DocumentIdType


@pytest.fixture
def subj_iso():
    return DocumentIdentifier(
        id="1111-2:2014",
        type=DocumentIdType.ISO)


def test_iso_remove_part(subj_iso):
    subj_iso.remove_part()
    assert subj_iso.id == "1111:2014"
    subj_iso.all_parts()
    assert subj_iso.id == "1111:2014 (all parts)"


def test_iso_remove_date(subj_iso):
    subj_iso.remove_date()
    subj_iso.id == "1111-2"


@pytest.fixture
def subj_urn_iso():
    return DocumentIdentifier(
        id="urn:iso:std:iso:1111:-1:stage-60.60:ed-1:v1:en,fr",
        type=DocumentIdType.URN)


def test_urn_iso_remove_part(subj_urn_iso):
    subj_urn_iso.remove_part()
    subj_urn_iso.id == "urn:iso:std:iso:1111"


@pytest.fixture
def subj_urn_iec():
    return DocumentIdentifier(
        type=DocumentIdType.URN,
        id="urn:iec:std:iec:61058-2-4:1995::csv:en:plus:amd:1:2003")


def test_urn_iec_remove_part(subj_urn_iec):
    subj_urn_iec.remove_part()
    subj_urn_iec.id = "urn:iec:std:iec:61058:1995::csv:en:plus:amd:1:2003"


def test_urn_iec_remove_date(subj_urn_iec):
    subj_urn_iec.remove_date()
    subj_urn_iec.id == "urn:iec:std:iec:61058-2-4:::csv:en:plus:amd:1:2003"


def test_urn_iec_set_all_parts(subj_urn_iec):
    subj_urn_iec.all_parts()
    subj_urn_iec.id == "urn:iec:std:iec:61058-2-4:1995::ser"


@pytest.fixture
def subj_gb():
    return DocumentIdentifier(
        id="1111.2-2014",
        type="Chinese Standard")  # test string not enum


def test_gb_remove_part(subj_gb):
    subj_gb.remove_part()
    subj_gb.id == "1111-2014"


def test_gb_remove_date(subj_gb):
    subj_gb.remove_date()
    subj_gb.id == "1111.2"


def test_to_xml(subj_iso):
    host = ET.Element("host")
    result = subj_iso.to_xml(host)

    assert result.attrib["type"] == "ISO"
    assert result.text == "1111-2:2014"


def test_to_asciibib(subj_urn_iso):
    result = subj_urn_iso.to_asciibib()

    assert result == inspect.cleandoc(
        """docid.type:: URN
           docid.id:: urn:iso:std:iso:1111:-1:stage-60.60:ed-1:v1:en,fr""")


def test_to_asciibib_with_pref(subj_urn_iec):
    result = subj_urn_iec.to_asciibib(prefix="test")

    assert result == inspect.cleandoc("""
        test.docid.type:: URN
        test.docid.id:: urn:iec:std:iec:61058-2-4:1995::csv:en:plus:amd:1:2003
        """)


def test_hash(subj_gb):
    result = dataclasses.asdict(subj_gb)

    assert result["type"] == "Chinese Standard"
    assert result["scope"] is None
