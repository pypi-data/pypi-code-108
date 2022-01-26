# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfield for calculating the ``is_open`` property of a request."""

from invenio_records_resources.records.systemfields.calculated import CalculatedField

from ...customizations.base.states import RequestState


class RequestStateCalculatedField(CalculatedField):
    """Systemfield for calculating if the request is in the expected state."""

    def __init__(self, key=None, expected_state=RequestState.OPEN):
        """Constructor."""
        super().__init__(key=key, use_cache=False)
        self._expected_state = expected_state

    def calculate(self, record):
        """Check if the request's status is mapped to the expected state."""
        status = getattr(record, self.key)
        set_state = record.type.available_statuses.get(status, None)
        return set_state == self._expected_state
