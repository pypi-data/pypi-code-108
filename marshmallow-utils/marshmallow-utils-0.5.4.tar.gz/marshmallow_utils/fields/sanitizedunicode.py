# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2021 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sanitized Unicode string field."""

from marshmallow import fields

from ..html import sanitize_unicode


class SanitizedUnicode(fields.String):
    """String field that sanitizes and fixes problematic unicode characters."""

    UNWANTED_CHARACTERS = {
        # Zero-width space
        u'\u200b',
    }

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize sanitized string value."""
        value = super()._deserialize(
            value, attr, data, **kwargs)
        return sanitize_unicode(value, unwanted_chars=self.UNWANTED_CHARACTERS)
