# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Marshmallow fields for search parameter deserialization."""

from marshmallow import fields


class ReferenceString(fields.Field):
    """Field for serializing reference querystring parameters into reference dicts.

    Reference querystring parameters are of the shape ``"TYPE:ID"``, which are
    deserialized into reference dicts of the shape ``{"TYPE": "ID"}``.
    """

    #: Default error messages.
    default_error_messages = {
        "invalid": "Not a valid reference.",
    }

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize reference string into a dict."""
        if value is None:
            return None
        elif ":" not in value:
            raise self.make_error("invalid")

        # if there's multiple colons, we assume the first one is the separator
        type_, id_ = value.split(":", 1)
        return {type_: id_}

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize the reference dict to a reference string."""
        # TODO do we even need this?
        if not isinstance(value, dict) or len(value) != 1:
            # a reference dict needs to have exactly one key
            raise self.make_error("invalid")

        key, value = list(value.items())[0]
        return f"{key}:{value}"
