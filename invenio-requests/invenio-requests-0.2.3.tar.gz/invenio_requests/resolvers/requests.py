# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2022 TU Wien.
# Copyright (C) 2021 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resolver and proxy for requests."""

from invenio_records_resources.references.resolvers.base import (
    EntityProxy,
    EntityResolver,
)
from sqlalchemy.exc import StatementError
from sqlalchemy.orm.exc import NoResultFound

from ..records.api import Request


class RequestProxy(EntityProxy):
    """Resolver proxy for a Request entity."""

    def _resolve(self):
        """Resolve the Request from the proxy's reference dict."""
        request_id = self._parse_ref_dict_id(self._ref_dict)
        try:
            return Request.get_record(request_id)
        except StatementError as exc:
            raise NoResultFound() from exc

    def get_need(self):
        """Return None since Needs are not applicable to requests."""
        return None


class RequestResolver(EntityResolver):
    """Resolver for requests."""

    type_id = "request"

    def matches_entity(self, entity):
        """Check if the entity is a request."""
        return isinstance(entity, Request)

    def _reference_entity(self, entity):
        """Create a reference dict for the given request."""
        id_ = entity.number if entity.number is not None else entity.id
        return {"request": str(id_)}

    def matches_reference_dict(self, ref_dict):
        """Check if the reference dict references a request."""
        return self._parse_ref_dict_type(ref_dict) == "request"

    def _get_entity_proxy(self, ref_dict):
        """Return a RequestProxy for the given reference dict."""
        return RequestProxy(ref_dict)
