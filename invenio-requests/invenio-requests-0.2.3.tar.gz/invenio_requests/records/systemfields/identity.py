# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identity systemfield."""

from invenio_records.systemfields import ModelField


class IdentityField(ModelField):
    """Systemfield for managing the request's number."""

    def assign(self, record, **kwargs):
        """Generate and assign a new identifier if none is set yet."""
        try:
            value = getattr(record.model, self.model_field_name)
        except AttributeError:
            value = None

        if value is None:
            value = record.type.generate_request_number(record, **kwargs)
            self._set(record.model, value)

        return value
