# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Datetime field which converts naive datetimes to TZ aware datetimes."""

from datetime import timezone

from marshmallow import fields


class TZDateTime(fields.DateTime):
    """Datetime field which converts naive datetimes to TZ aware datetimes.

    Defaults to setting the timezone to UTC, and using ISO format.
    """

    def __init__(self, timezone=timezone.utc, format='iso', **kwargs):
        """Initialize the field."""
        super().__init__(format=format, **kwargs)
        self.timezone = timezone

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize a datetime to add the timezone (UTC)."""
        if value is not None:
            value = value.replace(tzinfo=self.timezone)
        return super()._serialize(value, attr, obj, **kwargs)
