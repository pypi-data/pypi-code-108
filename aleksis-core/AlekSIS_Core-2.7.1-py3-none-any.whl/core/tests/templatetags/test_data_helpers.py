import json

import pytest

from aleksis.core.templatetags.data_helpers import get_dict, parse_json, verbose_name

pytestmark = pytest.mark.django_db


def test_get_dict_object():
    class _Foo(object):
        bar = 12

    assert _Foo.bar == get_dict(_Foo, "bar")


def test_get_dict_dict():
    _foo = {"bar": 12}

    assert _foo["bar"] == get_dict(_foo, "bar")


def test_get_dict_list():
    _foo = [10, 11, 12]

    assert _foo[2] == get_dict(_foo, 2)


def test_get_dict_invalid():
    _foo = 12

    assert get_dict(_foo, "bar") is None


def test_verbose_name_model():
    assert verbose_name("core", "person") == "Person"


def test_verbose_name_field():
    assert verbose_name("core", "person", "first_name") == "First Name"


def test_parse_json_json():
    foo = {"foo": 12, "bar": "12", "baz": []}
    foo_json = json.dumps(foo)

    assert parse_json(foo_json) == foo
    assert parse_json("{}") == {}


def test_parse_json_empty():
    assert parse_json(None) is None
    assert parse_json("") is None
