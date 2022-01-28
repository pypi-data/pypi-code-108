# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test LinksStore."""

import pytest
from marshmallow import Schema
from uritemplate import URITemplate

from marshmallow_utils import fields
from marshmallow_utils.links import LinksFactory


@pytest.fixture()
def my_schema():
    """A test schema with."""
    class LinksSchema(Schema):
        self = fields.Link(
            template=URITemplate("/records{?params*}"),
            params=lambda o: {"params": {
                # type is expected to show in the query string as type=A&type=B
                "type": ["A", "B"],
                "sort": "newest",
                "subtype": ["1"],
                "size": 10,
            }}
        )
        publish = fields.Link(
            template=URITemplate("/admin{/pid}"),
            params=lambda o: {"pid": o.get("pid")},
            permission="admin",
        )
        prev = fields.Link(
            template=URITemplate("/prev"),
            params=lambda o: {},
            when=lambda o: o.get("allowed", True)
        )

    class MySchema(Schema):
        links = fields.Links()

    factory = LinksFactory(
        host="localhost",
        config={"search": LinksSchema}
    )

    return MySchema(
        context={
            "links_factory": factory,
            "links_namespace": "search"

        }
    )


def test_links():
    """Test links factory with links field."""
    class EntitySchema(Schema):
        links = fields.Links()

    class ItemLinkSchema1(Schema):
        self = fields.Link(
            template=URITemplate("/1/{?pid}"),
            params=lambda o: {'pid': o.get("pid")},
            permission="read"
        )

    class ItemLinkSchema2(Schema):
        self = fields.Link(
            template=URITemplate("/2/{?pid}"),
            params=lambda o: {'pid': o.get("pid")},
            permission="create"
        )

    # Test: Create links during dumping
    f = LinksFactory(host="localhost", config={"item": ItemLinkSchema1})
    context = {
        "links_factory": f,
        "links_namespace": "item",
        "field_permission_check": lambda o: True  # allows anything
    }
    assert (
        {'links': {'self': 'https://localhost/1/?pid=1'}} ==
        EntitySchema(context=context).dump({"pid": 1})
    )

    # Test: Create links with other config during dumping
    f = LinksFactory(host="localhost", config={"item": ItemLinkSchema2})
    context = {
        "links_factory": f,
        "links_namespace": "item",
        "field_permission_check": lambda o: True  # allows anything
    }
    assert (
        {'links': {'self': 'https://localhost/2/?pid=1'}} ==
        EntitySchema(context=context).dump({"pid": 1})
    )


def test_params_expansion(my_schema):
    """Test link store resolver."""
    # Test self link generation with expansion of the "type" query string
    # argument.
    self_link = my_schema.dump({})["links"]["self"]
    assert self_link == \
        "https://localhost/records?size=10&sort=newest&subtype=1&type=A&type=B"


def test_unknown_namespace(my_schema):
    """Test unknown namespace."""
    my_schema.context["links_namespace"] = "unknown"
    assert my_schema.dump({})["links"] == {}


def test_permission(my_schema):
    """Test permission checks."""
    my_schema.context["field_permission_check"] = lambda a: a != "admin"
    links = my_schema.dump({})["links"]
    assert 'self' in links
    assert 'publish' not in links

    my_schema.context["field_permission_check"] = lambda a: True
    links = my_schema.dump({})["links"]
    assert 'self' in links
    assert 'publish' in links


def test_when(my_schema):
    links = my_schema.dump({"allowed": False})["links"]
    assert 'self' in links
    assert 'publish' in links
    assert 'prev' not in links

    links = my_schema.dump({"allowed": True})["links"]
    assert 'self' in links
    assert 'publish' in links
    assert 'prev' in links


def test_link_field_initialization():
    """Test that you can pass both URI templates and strings."""
    tpls = ["/records{?params*}", URITemplate("/records{?params*})")]
    for t in tpls:
        assert isinstance(fields.Link(template=t).template, URITemplate)
