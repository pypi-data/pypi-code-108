# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Request type systemfield for request records."""

import inspect

from invenio_records.systemfields import SystemField

from ...customizations.base import RequestType
from ...proxies import current_registry


class RequestTypeField(SystemField):
    """Systemfield for managing the request type."""

    def __init__(self, key="type"):
        """Constructor."""
        super().__init__(key)

    def set_obj(self, instance, obj):
        """Set the request type."""
        assert isinstance(obj, RequestType)

        self.set_dictkey(instance, obj.type_id)
        self._set_cache(instance, obj)

    def __set__(self, record, value):
        """Set the request type."""
        assert record is not None

        if inspect.isclass(value):
            # if a class was passed rather than an instance, try to instantiate it
            value = value()

        if not isinstance(value, RequestType):
            raise TypeError(f"Expected 'RequestType' but got: '{type(value)}'")

        self.set_obj(record, value)

    def obj(self, instance):
        """Get the request type."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        type_id = self.get_dictkey(instance)
        obj = current_registry.lookup(type_id)

        self._set_cache(instance, obj)
        return obj

    def __get__(self, record, owner=None):
        """Get the request type."""
        if record is None:
            # access by class
            return self

        return self.obj(record)
