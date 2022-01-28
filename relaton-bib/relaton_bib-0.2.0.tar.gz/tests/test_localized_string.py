import pytest

import xml.etree.ElementTree as ET

from relaton_bib import LocalizedString


def test_missin_props():
    with pytest.raises(ValueError) as excinfo:
        LocalizedString(None)
    assert "invalid LocalizedString content type: NoneType" \
        in str(excinfo.value)


def test_not_empty():
    loc_str = LocalizedString(
        "content & character to escape", "en", "Latn")
    assert len(loc_str) != 0


def test_xml_ampersand_escaped():
    loc_str = LocalizedString(
        "content & character to escape", "en", "Latn")

    host = ET.Element("host")
    result = loc_str.to_xml(host)

    assert result.attrib["language"] == "en"
    assert result.attrib["script"] == "Latn"

    xmlstr = ET.tostring(result, encoding='unicode', method='xml')

    assert "content &amp;amp; character to escape" in xmlstr
