import pytest
from xmldt.element import Element


def test_getters():
    element = Element("tag", {}, "contents")
    assert element.tag == "tag"
    assert element.contents == "contents"
    assert element["something"] is None


def test_setters():
    element = Element("foo", {}, "bar")
    element.tag = "tag"
    element["id"] = "ID"
    element.contents = "contents"
    assert element.tag == "tag"
    assert element.contents == "contents"
    assert element["id"] == "ID"


def test_short_setters():
    element = Element("foo", {}, "bar")
    element.q = "tag"
    element.v["id"] = "ID"
    element.c = "contents"
    assert element.q == "tag"
    assert element.c == "contents"
    assert element.v["id"] == "ID"


def test_toxml1():
    element = Element("foo", {}, "")
    assert element.xml == "<foo/>"


def test_toxml2():
    element = Element("foo", dict(bar="zbr"), "")
    assert element.xml == """<foo bar="zbr"/>"""


def test_toxml3():
    element = Element("foo", {}, "bar")
    assert element.xml == """<foo>bar</foo>"""


def test_toxml4():
    element = Element("foo", dict(bar="zbr"), "contents")
    assert element.xml == """<foo bar="zbr">contents</foo>"""

def test_toxml5():   ## toxml com tag= v= c=
    e = Element("foo", {"bar":"zbr"}, "contents")
    assert e.toxml() == """<foo bar="zbr">contents</foo>"""
    assert e.toxml(tag="XXX") == """<XXX bar="zbr">contents</XXX>"""
    assert e.toxml(c="XXX") == """<foo bar="zbr">XXX</foo>"""
    assert e.toxml(tag="T",v={},c="XXX") == """<T>XXX</T>"""


def test_father_is_none():
    element = Element("foo", dict(bar="zbr"), "contents")
    assert element._dt is None


def test_attrs():
    element = Element("foo", dict(bar="zbr"), "contents")
    attrs = element.attrs
    attrs["bar"] = "bar"
    assert element.xml == '<foo bar="bar">contents</foo>'


