# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Date string field."""

import arrow
from arrow.parser import ParserError
from marshmallow import fields, missing


class ISODateString(fields.Date):
    """ISO8601-formatted date string.

    ISODateString serializes to a date string and if it can't, the field is
    ignored (missing).

    NOTE: It serializes None to None.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize an ISO8601-formatted date."""
        # WHY: arrow.get(None) returns a date but we don't want it to
        if value is None:
            return missing

        try:
            return super()._serialize(
                arrow.get(value).date(), attr, obj, **kwargs)
        except ParserError:
            return missing

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize an ISO8601-formatted date."""
        return super()._deserialize(value, attr, data, **kwargs).isoformat()
