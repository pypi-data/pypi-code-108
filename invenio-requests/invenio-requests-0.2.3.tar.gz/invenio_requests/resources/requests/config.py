# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests resource config."""


import marshmallow as ma
from invenio_records_resources.resources import (
    RecordResourceConfig,
    SearchRequestArgsSchema,
)

from .fields import ReferenceString


#
# Request args
#
class RequestSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Add parameter to parse tags."""

    created_by = ReferenceString()
    topic = ReferenceString()
    receiver = ReferenceString()


#
# Resource config
#
class RequestsResourceConfig(RecordResourceConfig):
    """Requests resource configuration."""

    blueprint_name = "requests"
    url_prefix = "/requests"
    routes = {
        "list": "/",
        "item": "/<id>",
        "action": "/<id>/actions/<action>",
    }

    request_view_args = {
        "id": ma.fields.Str(),
        "action": ma.fields.Str(),
    }

    request_search_args = RequestSearchRequestArgsSchema
