import dataclasses
import datetime
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import CopyrightAssociation, ContributionInfo, Organization


@pytest.fixture
def subject():
    return CopyrightAssociation(
        from_=datetime.date(1990, 7, 26),
        owner=[
            ContributionInfo(role=[], entity=Organization(name="org1")),
            ContributionInfo(role=[], entity=Organization(name="org2"))
        ],
        scope="scope")


@pytest.fixture
def subject2():
    return CopyrightAssociation(from_="1991", owner=[
        ContributionInfo(role=[], entity=Organization(name="org3")),
        ContributionInfo(role=[], entity=Organization(name="org4"))]
    )


def test_error_empty_owners():
    with pytest.raises(ValueError) as excinfo:
        CopyrightAssociation(from_="2019", owner=[])
    assert "at least one owner should exist." \
        in str(excinfo.value)


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert host.find("./copyright/from").text == "1990"
    assert len(host.findall("./copyright/owner")) == 2
    assert host.find("./copyright/scope").text == "scope"


def test_to_xml_2(subject2):
    host = ET.Element("host")
    result = subject2.to_xml(host)

    assert host.find("./copyright/from").text == "1991"
    assert len(host.findall("./copyright/owner/organization")) == 2
    assert host.find("./copyright/scope") is None


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """copyright::
           copyright.owner.name:: org1
           copyright.role.type:: publisher
           copyright::
           copyright.owner.name:: org2
           copyright.role.type:: publisher
           copyright.from:: 1990
           copyright.scope:: scope""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="tst")

    # role have no copyright because of logic in contribution_info.py:87
    assert result == inspect.cleandoc(
        """tst::
           tst.copyright.owner.name:: org1
           tst.role.type:: publisher
           tst::
           tst.copyright.owner.name:: org2
           tst.role.type:: publisher
           tst.copyright.from:: 1990
           tst.copyright.scope:: scope""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert type(result["from_"]) is datetime.date
    assert result["scope"] == "scope"
