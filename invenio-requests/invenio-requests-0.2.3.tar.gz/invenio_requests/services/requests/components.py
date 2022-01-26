# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Component for creating request numbers."""

from invenio_records_resources.services.records.components import (
    DataComponent,
    ServiceComponent,
)


class RequestNumberComponent(ServiceComponent):
    """Component for assigning request numbers to new requests."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Create identifier when record is created."""
        type(record).number.assign(record)


class EntityReferencesComponent(ServiceComponent):
    """Component for initializing a request's entity references."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Initialize the entity reference fields of a request."""
        for field in ("created_by", "receiver", "topic"):
            if field in kwargs:
                setattr(record, field, kwargs[field])


class RequestDataComponent(DataComponent):
    """Request variant of DataComponent using dynamic schema."""

    def update(self, identity, data=None, record=None, **kwargs):
        """Update an existing record (request)."""
        # Clear any top-level field not set in the data.
        # Note: This ensures that if a user removes a top-level key, then we
        # also remove it from the record (since record.update() doesn't take
        # care of this). Removal of subkeys is not an issue as the
        # record.update() will update the top-level key.
        schema = record.type.marshmallow_schema()
        fields = set(schema().fields.keys())
        data_fields = set(data.keys())
        for f in fields - data_fields:
            if f in record:
                del record[f]
        # Update the remaining keys.
        record.update(data)
        # Clear None values from the record.
        record.clear_none()


class DefaultStatusComponent(ServiceComponent):
    """Component for initializing the default status of the request."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Initialize the default status of the request."""
        record.status = record.type.default_status
