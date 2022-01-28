import dataclasses
import inspect
import logging
import xml.etree.ElementTree as ET

from relaton_bib import BibItemLocality, BibItemLocalityType


def test_to_xml_all_props():
    bib_item = BibItemLocality(
        type=BibItemLocalityType.SECTION.value,
        reference_from="from",
        reference_to="to")

    host = ET.Element("host")
    result = bib_item.to_xml(host)

    assert result.attrib["type"] == BibItemLocalityType.SECTION.value
    assert host.find("./referenceFrom").text == "from"
    assert host.find("./referenceTo").text == "to"


def test_to_xml_only_required_props():
    bib_item = BibItemLocality(
        type=BibItemLocalityType.CLAUSE.value,
        reference_from="from")

    host = ET.Element("host")
    result = bib_item.to_xml(host)

    assert result.attrib["type"] == BibItemLocalityType.CLAUSE.value
    assert host.find("./referenceFrom").text == "from"
    assert host.find("./referenceTo") is None


def test_invalid_locality_type(caplog):
    invalid = "invalid"

    with caplog.at_level(logging.WARNING):
        BibItemLocality(type=invalid, reference_from="from")

    assert f"[relaton-bib] invalid locality type: {invalid}" in caplog.text


def test_custom_locality_type(caplog):
    custom = "locality:custom"

    with caplog.at_level(logging.WARNING):
        BibItemLocality(type=custom, reference_from="from")

    assert f"[relaton-bib] invalid locality type: {custom}" not in caplog.text


def test_to_asciibib_all_props():
    bib_item = BibItemLocality(
        type=BibItemLocalityType.SECTION.value,
        reference_from="from",
        reference_to="to")

    result = bib_item.to_asciibib(prefix="test")

    assert result == inspect.cleandoc("""test.type:: section
                                      test.reference_from:: from
                                      test.reference_to:: to""")


def test_to_asciibib_only_required_props():
    bib_item = BibItemLocality(
        type=BibItemLocalityType.SECTION.value,
        reference_from="from")

    result = bib_item.to_asciibib(count=2)

    assert result == inspect.cleandoc("""::
                                      type:: section
                                      reference_from:: from""")


def test_hash_all_props():
    bib_item = BibItemLocality(
        type=BibItemLocalityType.SECTION.value,
        reference_from="from",
        reference_to="to")

    result = dataclasses.asdict(bib_item)

    assert result["type"] == BibItemLocalityType.SECTION.value
    assert result["reference_from"]["content"] == "from"
    assert result["reference_to"]["content"] == "to"


def test_hash_only_required_props():
    bib_item = BibItemLocality(
        type=BibItemLocalityType.SECTION.value,
        reference_from="from")

    result = dataclasses.asdict(bib_item)

    assert result["type"] == BibItemLocalityType.SECTION.value
    assert result["reference_from"]["content"] == "from"
