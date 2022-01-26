# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Results for the requests service."""

from invenio_records_resources.services.records.results import RecordItem, RecordList


class RequestItem(RecordItem):
    """Single request result."""

    def __init__(
        self,
        service,
        identity,
        request,
        errors=None,
        links_tpl=None,
        schema=None,
    ):
        """Constructor."""
        self._data = None
        self._errors = errors
        self._identity = identity
        self._request = request
        self._service = service
        self._links_tpl = links_tpl
        self._schema = schema or service._wrap_schema(request.type.marshmallow_schema())

    @property
    def id(self):
        """Identity of the request."""
        return str(self._request.id)

    def __getitem__(self, key):
        """Key a key from the data."""
        self.data[key]

    @property
    def links(self):
        """Get links for this result item."""
        return self._links_tpl.expand(self._request, identity=self._identity)

    @property
    def _obj(self):
        """Return the object to dump."""
        return self._request

    @property
    def data(self):
        """Property to get the request."""
        if self._data:
            return self._data

        self._data = self._schema.dump(
            self._obj,
            context={
                "identity": self._identity,
                "record": self._request,
            },
        )

        if self._links_tpl:
            self._data["links"] = self.links

        return self._data

    @property
    def errors(self):
        """Get the errors."""
        return self._errors

    def to_dict(self):
        """Get a dictionary for the request."""
        res = self.data
        if self._errors:
            res["errors"] = self._errors
        return res


class RequestList(RecordList):
    """List of request results."""

    def __init__(
        self,
        service,
        identity,
        results,
        params=None,
        links_tpl=None,
        links_item_tpl=None,
    ):
        """Constructor.

        :params service: a service instance
        :params identity: an identity that performed the service request
        :params results: the search results
        :params params: dictionary of the query parameters
        """
        self._identity = identity
        self._results = results
        self._service = service
        self._params = params
        self._links_tpl = links_tpl
        self._links_item_tpl = links_item_tpl

    @property
    def hits(self):
        """Iterator over the hits."""
        request_cls = self._service.record_cls

        for hit in self._results:
            # load dump
            request = request_cls.loads(hit.to_dict())
            schema = self._service._wrap_schema(request.type.marshmallow_schema())

            # project the request
            projection = schema.dump(
                request,
                context={
                    "identity": self._identity,
                    "record": request,
                },
            )

            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    request, identity=self._identity
                )

            yield projection

    def to_dict(self):
        """Return result as a dictionary."""
        # TODO: This part should imitate the result item above. I.e. add a
        # "data" property which uses a ServiceSchema to dump the entire object.
        res = {
            "hits": {
                "hits": list(self.hits),
                "total": self.total,
            }
        }
        if self.aggregations:
            res["aggregations"] = self.aggregations

        if self._params:
            res["sortBy"] = self._params["sort"]
            if self._links_tpl:
                res["links"] = self._links_tpl.expand(self.pagination)

        return res
