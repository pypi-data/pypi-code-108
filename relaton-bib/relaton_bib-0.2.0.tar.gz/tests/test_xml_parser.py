import os
import logging
import xml.etree.ElementTree as ET

from . import elements_equal
from relaton_bib import LocalityStack, SourceLocalityStack, from_xml


def test_creates_item_from_xml():
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "bib_item.xml")
    reference = ET.parse(file)

    item = from_xml(reference)

    assert item is not None
    assert elements_equal(reference.getroot(), item.to_xml())


def test_creates_item_from_bibdata_xml():
    file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "examples",
                        "bibdata_item.xml")

    tree = ET.parse(file)
    reference = tree.getroot()

    item = from_xml(reference)
    assert item is not None

    result = item.to_xml(opts=dict(bibdata=True))
    assert elements_equal(reference, result)


def test_parse_date_from():
    item_xml = """<bibitem id="id">
                    <title type="main">Title</title>
                    <date type="circulated"><from>2001-02-03</from></date>
                  </bibitem>"""
    item_note = ET.fromstring(item_xml)
    item = from_xml(item_note)
    assert item.date[0].value("from_") == "2001-02-03"


def test_parse_locality_not_inclosed_in_localityStack():
    item_xml = """
        <bibitem id="id">
            <title type="main">Title</title>
            <relation type="updates">
            <bibitem>
                <formattedref format="text/plain">ISO 19115</formattedref>
            </bibitem>
            <locality type="section">
                <referenceFrom>Reference from</referenceFrom>
            </locality>
            </relation>
        </bibitem>"""
    item_note = ET.fromstring(item_xml)
    item = from_xml(item_note)
    assert type(item.relation[0].locality[0]) is LocalityStack


def test_parse_sourceLocality_not_inclosed_in_sourceLocalityStack():
    item_xml = """
        <bibitem id="id">
          <title type="main">Title</title>
          <relation type="updates">
            <bibitem>
              <formattedref format="text/plain">ISO 19115</formattedref>
            </bibitem>
            <sourceLocality type="section">
              <referenceFrom>Reference from</referenceFrom>
            </sourceLocality>
          </relation>
        </bibitem>"""
    item_note = ET.fromstring(item_xml)
    item = from_xml(item_note)
    assert type(item.relation[0].source_locality[0]) is SourceLocalityStack


def test_ignore_empty_dates():
    item_xml = """
        <bibitem id="id">
            <title type="main">Title</title>
            <date type="circulated" />
        </bibitem>"""
    item_note = ET.fromstring(item_xml)
    item = from_xml(item_note)
    assert len(item.date) == 0


def test_warn_if_XML_empty(caplog):
    item = None
    with caplog.at_level(logging.WARNING):
        item = from_xml(ET.Element("test"))

    assert "can't find bibitem" in caplog.text
    assert item is None
