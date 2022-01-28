from __future__ import annotations
import dataclasses
import logging
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import FormattedString, ContributorRole, \
    ContributionInfo, Organization


@pytest.fixture
def role():
    return ContributorRole(type="type", description=[
        FormattedString("first"),
        FormattedString("second"),
        FormattedString("third")
    ])


@pytest.fixture
def info(role):
    return ContributionInfo(
        role=[role],
        entity=Organization(name="test"))


def test_role_invalid_type(caplog):
    invalid = "invalid"

    with caplog.at_level(logging.WARNING):
        ContributorRole(type=invalid)

    assert f"[relaton-bib] Contributor's type {invalid} is invalid" \
        in caplog.text


def test_role_to_xml(role):
    host = ET.Element("host")
    result = role.to_xml(host)

    assert result.attrib["type"] == "type"
    assert len(host.findall("./role/description")) == 3


def test_role_to_asciibib(role):
    result = role.to_asciibib()

    assert result == inspect.cleandoc(
        """role.description::
           role.description.content:: first
           role.description.format:: text/plain
           role.description::
           role.description.content:: second
           role.description.format:: text/plain
           role.description::
           role.description.content:: third
           role.description.format:: text/plain
           role.type:: type""")


def test_role_to_asciibib_with_pref(role):
    result = role.to_asciibib(prefix="test")

    assert result == inspect.cleandoc(
        """test.role.description::
           test.role.description.content:: first
           test.role.description.format:: text/plain
           test.role.description::
           test.role.description.content:: second
           test.role.description.format:: text/plain
           test.role.description::
           test.role.description.content:: third
           test.role.description.format:: text/plain
           test.role.type:: type""")


def test_role_hash(role):
    result = dataclasses.asdict(role)

    assert result["type"] == "type"
    assert len(result["description"]) == 3


def test_info_to_xml(info):
    host = ET.Element("host")
    result = info.to_xml(host)

    assert host.find("./organization/name").text == "test"


def test_info_to_asciibib(info):
    result = info.to_asciibib()

    assert result == inspect.cleandoc(
        """name:: test
           role.description::
           role.description.content:: first
           role.description.format:: text/plain
           role.description::
           role.description.content:: second
           role.description.format:: text/plain
           role.description::
           role.description.content:: third
           role.description.format:: text/plain
           role.type:: type""")


def test_info_to_asciibib_with_pref(info):
    result = info.to_asciibib(prefix="test")

    assert result == inspect.cleandoc(
        """test.name:: test
           test.role.description::
           test.role.description.content:: first
           test.role.description.format:: text/plain
           test.role.description::
           test.role.description.content:: second
           test.role.description.format:: text/plain
           test.role.description::
           test.role.description.content:: third
           test.role.description.format:: text/plain
           test.role.type:: type""")


def test_info_hash(info):
    result = dataclasses.asdict(info)

    assert result["entity"]["name"][0]["content"] == "test"
    assert len(result["role"][0]["description"]) == 3
