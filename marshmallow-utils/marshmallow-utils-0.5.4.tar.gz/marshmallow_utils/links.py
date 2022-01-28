# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Link store and field for generating links."""

from collections import defaultdict

from marshmallow import Schema, fields, missing, post_dump
from uritemplate import URITemplate
from werkzeug.datastructures import MultiDict


def _unpack_dict(data):
    """Unpack lists inside a dict.

    For instance this dictionary:

    .. code-block:: python

        {
            "type": ["A", "B"],
            "sort": "newest",
        }

    Is expanded to:

    .. code-block:: python

        [
            ("sort", "newest"),
            ("type", "A"),
            ("type", "B"),
        ]
    """
    for key, value in sorted(data.items()):
        if isinstance(value, list):
            for v in value:
                yield key, v
        else:
            yield key, value


class LinksFactory:
    """Utility class for keeping track of and resolve links.

    :params host: A hostname or a callable returning a hostname.
    :params config: A link configuration.
    """

    def __init__(self, host=None, config=None):
        """Constructor."""
        self._host = host
        self._config = config or {}

    def get_schema(self, namespace, context):
        """Get the schema for a given namespace."""
        schema = self._config.get(namespace)
        if schema:
            return schema(context=context or {})
        return schema

    @property
    def host(self):
        """Get the hostname."""
        return self._host() if callable(self._host) else self._host

    def create_link(self, template, vars):
        """Create the link template with the template variables.

        :param template: URITemplate to expand.
        :param vars: The template variables for the expansion.
        """
        return self.base_url(
            host=self.host,
            rendered_path=template.expand(**self.preprocess_vars(vars))
        )

    @staticmethod
    def preprocess_vars(vars):
        """Preprocess template variables before expansion."""
        for k, v in vars.items():
            if isinstance(v, MultiDict):
                vars[k] = list(sorted(v.items(multi=True)))
            elif isinstance(v, dict):
                # Note, we unpack dicts with list values at this level, because
                # there are no meaningful templates that can make use of them
                # (basically the lists just becomes URL encoded python objects)
                vars[k] = list(_unpack_dict(v))
        return vars

    @staticmethod
    def base_url(scheme="https", host=None, rendered_path="/"):
        """Creates the URL for API and UI endpoints."""
        if host and scheme:
            assert rendered_path.startswith("/")
            return f"{scheme}://{host}{rendered_path}"
        else:
            return rendered_path
