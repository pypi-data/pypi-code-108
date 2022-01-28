import dataclasses
import inspect
import pytest

import xml.etree.ElementTree as ET

from relaton_bib import Address, Contact, ContactType, Contributor


@pytest.fixture
def subject():
    return Contributor(
        uri="https://contributor.uri",
        contact=[
            # all props
            Address(
                street=["street", "1", "/2"],
                city="NY",
                country="USA",
                state="NY",
                postcode="10001"),
            # only required props
            Address(
                street=["vulica", "3", "/4"],
                city="MSQ",
                country="BY"),
            Contact(
                type=ContactType.EMAIL.value,
                value="test@test.com")
        ])


def test_url_eq_uri(subject):
    assert subject.uri == subject.url


def test_to_xml(subject):
    host = ET.Element("host")
    result = subject.to_xml(host)

    assert len(host.findall(f"./{ContactType.EMAIL.value}")) == 1
    assert host.find(f"./{ContactType.EMAIL.value}").text == "test@test.com"

    assert len(host.findall("./address")) == 2
    assert host.find("./address/state").text == "NY"
    assert host.find("./address/postcode").text == "10001"
    assert host.find("./address/street[1]").text == "street"
    assert host.find("./address[2]/street[1]").text == "vulica"
    assert host.find("./address/city").text == "NY"
    assert host.find("./address[2]/city").text == "MSQ"


def test_to_asciibib(subject):
    result = subject.to_asciibib()

    assert result == inspect.cleandoc(
        """url:: https://contributor.uri
           address::
           address.street:: street
           address.street:: 1
           address.street:: /2
           address.city:: NY
           address.state:: NY
           address.country:: USA
           address.postcode:: 10001
           address::
           address.street:: vulica
           address.street:: 3
           address.street:: /4
           address.city:: MSQ
           address.country:: BY
           contact.type:: email
           contact.value:: test@test.com""")


def test_to_asciibib_with_pref(subject):
    result = subject.to_asciibib(prefix="test")

    assert result == inspect.cleandoc(
        """test.url:: https://contributor.uri
           test.address::
           test.address.street:: street
           test.address.street:: 1
           test.address.street:: /2
           test.address.city:: NY
           test.address.state:: NY
           test.address.country:: USA
           test.address.postcode:: 10001
           test.address::
           test.address.street:: vulica
           test.address.street:: 3
           test.address.street:: /4
           test.address.city:: MSQ
           test.address.country:: BY
           test.contact.type:: email
           test.contact.value:: test@test.com""")


def test_hash(subject):
    result = dataclasses.asdict(subject)

    assert result["uri"] == "https://contributor.uri"
    assert len(result["contact"]) == 3
