import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import Affiliation, Organization, Person, \
    FullName, PersonIdentifier


def test_fillname_without_args():
    with pytest.raises(ValueError) as excinfo:
        FullName()
    assert "Should be given surname or completename" \
        in str(excinfo.value)


def test_invalid_personal_id_type():
    with pytest.raises(ValueError) as excinfo:
        Person(
            name=FullName(completename="John Lennon"),
            identifier=[PersonIdentifier("wrong_type", "value")])
    assert 'Invalid type. It should be "isni" or "uri".' \
        in str(excinfo.value)


def test_missing_name():
    with pytest.raises(ValueError) as excinfo:
        Person(identifier=[PersonIdentifier("isni", "value")])
    assert "missing name" \
        in str(excinfo.value)


@pytest.fixture
def subject():
    return Person(
        name=FullName(completename="John Lennon"),
        identifier=[PersonIdentifier("isni", "isni-value")],
        affiliation=[Affiliation(
            Organization(name="org1")
        )]
    )


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert host.find("./person/name/completename").text == "John Lennon"
    assert result.find("./affiliation/organization/name").text == "org1"
    assert result.find("./identifier").text == "isni-value"
    assert result.find("./identifier").attrib["type"] == "isni"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """name.completename:: John Lennon
           affiliation.organization.name:: org1
           type:: isni
           value:: isni-value""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="t")

    assert result == inspect.cleandoc(
        """t.name.completename:: John Lennon
           t.affiliation.organization.name:: org1
           t.type:: isni
           t.value:: isni-value""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["identifier"][0]["type"] == "isni"
    assert result["name"]["completename"]["content"] == "John Lennon"
