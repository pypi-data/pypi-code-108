# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Status systemfield for request records."""

from invenio_records.systemfields import SystemField


class RequestStatusField(SystemField):
    """Systemfield for managing the request status."""

    def __set__(self, record, value):
        """Set the request's status."""
        assert record is not None

        if value not in record.type.available_statuses:
            raise ValueError(f"Unknown status: '{value}'")

        self.set_dictkey(record, value)

    def __get__(self, record, owner=None):
        """Get the request's status."""
        if record is None:
            # access by class
            return self

        status = self.get_dictkey(record)
        if status is None:
            statuses = list(record.type.available_statuses.keys())
            status = statuses[0] if statuses else None

        return status
