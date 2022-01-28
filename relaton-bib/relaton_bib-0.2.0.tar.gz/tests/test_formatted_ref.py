import pytest
import inspect

import dataclasses
import xml.etree.ElementTree as ET

from relaton_bib import FormattedRef, FormattedStringFormat


@pytest.fixture
def subject():
    return FormattedRef(content="content & character to escape",
                        language="en",
                        script="Latn",
                        format=FormattedStringFormat.TEXT_HTML.value)


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert result.attrib["format"] == FormattedStringFormat.TEXT_HTML.value
    assert result.attrib["language"] == "en"
    assert result.attrib["script"] == "Latn"

    xmlstr = ET.tostring(result, encoding='unicode', method='xml')

    assert "content &amp;amp; character to escape" in xmlstr


def test_to_asciibib(subject):
    assert subject.to_asciibib() == inspect.cleandoc(
        """formattedref.content:: content & character to escape
           formattedref.language:: en
           formattedref.script:: Latn
           formattedref.format:: text/html""")


def test_to_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["format"] == FormattedStringFormat.TEXT_HTML.value
    assert result["language"] == ["en"]
    assert result["script"] == ["Latn"]
    assert result["content"] == "content & character to escape"
