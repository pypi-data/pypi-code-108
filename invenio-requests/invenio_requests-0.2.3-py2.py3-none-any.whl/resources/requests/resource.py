# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests resource."""


from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import es_preference


#
# Resource
#
class RequestsResource(RecordResource):
    """Resource for generic requests."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            route("GET", routes["list"], self.search),
            route("GET", routes["item"], self.read),
            route("PUT", routes["item"], self.update),
            route("DELETE", routes["item"], self.delete),
            route("POST", routes["action"], self.execute_action),
        ]

    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the items."""
        hits = self.service.search(
            identity=g.identity,
            params=resource_requestctx.args,
            es_preference=es_preference(),
        )
        return hits.to_dict(), 200

    @request_view_args
    @response_handler()
    def read(self):
        """Read an item."""
        item = self.service.read(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
        )
        return item.to_dict(), 200

    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def update(self):
        """Update an item."""
        # TODO should we allow updating of requests in this general resource?
        item = self.service.update(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
            data=resource_requestctx.data,
        )
        return item.to_dict(), 200

    @request_headers
    @request_view_args
    def delete(self):
        """Delete an item."""
        self.service.delete(
            id_=resource_requestctx.view_args["id"],
            identity=g.identity,
        )
        return "", 204

    @request_view_args
    @request_headers
    @request_data
    @response_handler()
    def execute_action(self):
        """Execute action."""
        item = self.service.execute_action(
            identity=g.identity,
            id_=resource_requestctx.view_args["id"],
            action=resource_requestctx.view_args["action"],
            data=resource_requestctx.data
        )
        return item.to_dict(), 200
