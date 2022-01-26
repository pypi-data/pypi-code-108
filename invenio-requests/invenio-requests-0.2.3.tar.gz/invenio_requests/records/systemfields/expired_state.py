# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Systemfield for calculating the ``is_expired`` property of a request."""


from datetime import datetime

import pytz
from invenio_records_resources.records.systemfields.calculated import CalculatedField


class ExpiredStateCalculatedField(CalculatedField):
    """Systemfield for calculating whether or not the request is expired."""

    def __init__(self, key=None):
        """Constructor."""
        super().__init__(key=key, use_cache=False)

    def calculate(self, record):
        """Calculate the ``is_expired`` property of the request."""
        expires_at = getattr(record, self.key)

        # if 'expires_at' is not set, that means it doesn't expire
        if expires_at is None:
            return False

        # comparing timezone-aware and naive datetimes results in an error
        # https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive # noqa
        now = datetime.utcnow()
        if expires_at.tzinfo and expires_at.tzinfo.utcoffset(expires_at) is not None:
            now = now.replace(tzinfo=pytz.utc)

        return expires_at < now
