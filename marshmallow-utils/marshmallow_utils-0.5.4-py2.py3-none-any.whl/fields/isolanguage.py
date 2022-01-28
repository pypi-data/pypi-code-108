# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""ISO language string field."""

import pycountry
from marshmallow import ValidationError

from .sanitizedunicode import SanitizedUnicode


def _(x):
    return x


def validate_iso639_3(value):
    """Validate that language is ISO 639-3 value."""
    if not pycountry.languages.get(alpha_3=value):
        raise ValidationError(
            _('Language must be a lower-cased 3-letter ISO 639-3 string.'),
            field_name=['language']
        )


class ISOLangString(SanitizedUnicode):
    """ISO language string field."""

    def __init__(self, validate=validate_iso639_3, *args, **kwargs):
        """ISO language string field initialization."""
        super(ISOLangString, self).__init__(
            validate=validate, *args, **kwargs
        )
