# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""RequestEvent Resource Configuration."""

from invenio_records_resources.resources import RecordResourceConfig
from marshmallow import fields


class RequestCommentsResourceConfig(RecordResourceConfig):
    """Request Events resource configuration."""

    blueprint_name = "request_events"
    url_prefix = "/requests"
    routes = {
        "list": "/<request_id>/comments",
        "item": "/<request_id>/comments/<comment_id>",
        "timeline": "/<request_id>/timeline",
    }

    # Input
    # WARNING: These "request_*" values have nothing to do with the
    #          "Request" of "RequestEvent". They are related to the Flask
    #          request.
    request_list_view_args = {
        "request_id": fields.Str(),
    }
    request_item_view_args = {
        "request_id": fields.Str(),
        "comment_id": fields.Str(),
    }
