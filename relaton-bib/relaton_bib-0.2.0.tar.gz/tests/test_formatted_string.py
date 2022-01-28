import pytest
import inspect

import dataclasses
import xml.etree.ElementTree as ET

from relaton_bib import FormattedString, FormattedStringFormat


@pytest.fixture
def formatted_str():
    return FormattedString(content="content & character to escape",
                           language="en",
                           script="Latn",
                           format=FormattedStringFormat.TEXT_HTML.value)


def test_dafault_format():
    formatted_str = FormattedString(
        "content & character to escape", "en", "Latn")
    assert formatted_str.format == FormattedStringFormat.TEXT_PLAIN.value


def test_to_xml(formatted_str):
    host = ET.Element("host")
    result = formatted_str.to_xml(host)

    assert result.attrib["format"] == FormattedStringFormat.TEXT_HTML.value
    assert result.attrib["language"] == "en"
    assert result.attrib["script"] == "Latn"

    xmlstr = ET.tostring(result, encoding='unicode', method='xml')

    assert "content &amp;amp; character to escape" in xmlstr


def test_to_asciibib(formatted_str):
    assert formatted_str.to_asciibib() == inspect.cleandoc(
        """content:: content & character to escape
        language:: en
        script:: Latn
        format:: text/html""")


def test_to_hash(formatted_str):
    result = dataclasses.asdict(formatted_str)

    assert result["format"] == FormattedStringFormat.TEXT_HTML.value
    assert result["language"] == ["en"]
    assert result["script"] == ["Latn"]
    assert result["content"] == "content & character to escape"
