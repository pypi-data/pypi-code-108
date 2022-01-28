# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Extended Date(/Time) Format Level 0 date string field."""

from edtf import Date, Interval, parse_edtf
from edtf.parser.grammar import ParseException
from marshmallow import ValidationError, fields
from marshmallow.validate import Validator


class EDTFValidator(Validator):
    """EDTF validator."""

    default_message = "Please provide a valid date or interval."

    def __init__(self, types=[Date, Interval], chronological_interval=True,
                 error=None):
        """Constructor.

        :params types: List of EDTFObject subclasses that you accept. Use
            EDTFObject to accept all levels.
        """
        self._types = types or []
        self._chronological_interval = chronological_interval
        self._error = error or self.default_message

    def _format_error(self, value, e):
        return self._error.format(input=value, edtf=e)

    def __call__(self, value):
        """Validate."""
        try:
            e = parse_edtf(value)
        except ParseException:
            raise ValidationError(self._format_error(value, None))

        if self._types:
            if not any([isinstance(e, t) for t in self._types]):
                raise ValidationError(self._format_error(value, e))

        if self._chronological_interval:
            # We require intervals to be chronological. EDTF Date and Interval
            # both have same interface and
            # date.lower_strict() <= date.upper_strict() is always True for a
            # Date
            if e.upper_strict() < e.lower_strict():
                raise ValidationError(self._format_error(value, e))

        return value


class EDTFDateString(fields.Str):
    """
    Extended Date(/Time) Format Level 0 date string field.

    A string field which an using the EDTF Validator.
    """

    def __init__(self, **kwargs):
        """Constructor."""
        kwargs.setdefault('validate', EDTFValidator())
        super().__init__(**kwargs)
