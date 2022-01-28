import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import BibliographicItemVersion


@pytest.fixture
def subject():
    return BibliographicItemVersion(
        revision_date="01/01/2022",
        draft=["draft1", "2", "3"])


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert len(result.findall("./draft")) == 3
    assert host.find("./version/revision-date").text == "01/01/2022"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """version.revision_date:: 01/01/2022
           version.draft:: draft1
           version.draft:: 2
           version.draft:: 3""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="test")

    assert result == inspect.cleandoc(
        """test.version.revision_date:: 01/01/2022
           test.version.draft:: draft1
           test.version.draft:: 2
           test.version.draft:: 3""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert len(result["draft"]) == 3
    assert result["revision_date"] == "01/01/2022"
