# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identifier field."""

from marshmallow import ValidationError
from marshmallow.fields import List


class IdentifierSet(List):
    """Identifier list with deduplication.

    It assumes the items of the list contain a *scheme* property.
    """

    default_error_messages = {
        "multiple_values": "Only one identifier per scheme is allowed.",
    }

    def _validate(self, value):
        """Validates the list of identifiers."""
        schemes = [identifier["scheme"] for identifier in value]
        if not len(value) == len(set(schemes)):
            raise self.make_error(key="multiple_values")
