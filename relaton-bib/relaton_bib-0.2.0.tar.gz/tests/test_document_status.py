import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import DocumentStatus


def test_create_with_hash():
    ds = DocumentStatus(stage={"value": "30", "abbreviation": "CD"})
    assert type(ds.stage) is DocumentStatus.Stage
    assert ds.stage.value == "30"
    assert ds.stage.abbreviation == "CD"


@pytest.fixture
def subject():
    return DocumentStatus(
        stage=DocumentStatus.Stage(value="30", abbreviation="CD"),
        substage=DocumentStatus.Stage(value="90", abbreviation="DVD"),
        iteration="5")


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert host.find("./status") is not None
    assert result.find("./stage").text == "30"
    assert result.find("./stage").attrib["abbreviation"] == "CD"
    assert result.find("./substage").text == "90"
    assert result.find("./substage").attrib["abbreviation"] == "DVD"
    assert result.find("./iteration").text == "5"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """docstatus.stage:: 30
           docstatus.substage:: 90
           docstatus.iteration:: 5""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="uh")

    assert result == inspect.cleandoc(
        """uh.docstatus.stage:: 30
           uh.docstatus.substage:: 90
           uh.docstatus.iteration:: 5""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["iteration"] == "5"
    assert result["stage"]["value"] == "30"
    assert result["stage"]["abbreviation"] == "CD"
    assert result["substage"]["value"] == "90"
    assert result["substage"]["abbreviation"] == "DVD"
