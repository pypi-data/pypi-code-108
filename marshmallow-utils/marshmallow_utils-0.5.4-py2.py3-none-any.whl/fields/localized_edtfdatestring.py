# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Localized Extended Date(/Time) Format Level 0 date string field."""

import calendar
from datetime import date, datetime

from edtf.parser.grammar import Interval, ParseException, level0Expression
from marshmallow import fields


def _(x):
    return x

# TODO: move to external package and depend on flask-babelex


class LocalizedEDTFFormatter(object):
    """Localized Formatter for EDTF dates."""

    RANGE_SEPARATOR = u' \u2014 '
    AVAILABLE_FORMATS = ['short', 'medium', 'long', 'full']

    def __init__(self, format=None, locale=None):
        """EDTF formatter consrtuctor.

        :params format: One of `AVAILABLE_FORMATS`.
        :params locale: Locale value used for localization.
        """
        self.format = format or 'medium'
        self.locale = locale or 'en'

    def has_day_precision(self, edtfdate):
        """Check if EDTF date has `day` precision.

        If so, then the string can be converted to a python date object.
        """
        return edtfdate.precision == 'day'

    def to_date(self, edtfdate, strict="lower"):
        """Convert EDTF date to python date object.

        :params strict: Convert EDTF date string to `lower` or `upper` strict
                        in case it is not a `python.datetime` compatible value.
        """
        if self.has_day_precision(edtfdate):
            return datetime.strptime(edtfdate.isoformat(), "%Y-%m-%d").date()
        else:
            if strict == 'lower':
                edtfdate = edtfdate.lower_strict()
            elif strict == 'upper':
                edtfdate = edtfdate.upper_strict()
            return date.fromtimestamp(calendar.timegm(edtfdate))

    def format_date(self, edtfdate, strict):
        """Format single EDTF date."""
        try:
            # TODO: remove when moved to external package
            from flask_babelex import format_date
            date_obj = self.to_date(edtfdate, strict)
            return format_date(date_obj, self.format, self.locale)
        except ImportError:
            return str(edtfdate)

    def format_range_date(self, range_dates):
        """Format range of EDTF dates."""
        # TODO: remove when moved to external package
        try:
            from flask_babelex import format_date
            start_date = self.format_date(range_dates[0], strict="lower")
            end_date = self.format_date(range_dates[1], strict="upper")
            return self.RANGE_SEPARATOR.join([start_date, end_date])
        except ImportError:
            return self.RANGE_SEPARATOR.join(range_dates)


class LocalizedEDTFDateString(fields.Str):
    """
    Localized Extended Date(/Time) Format Level 0 date string field.

    Made a field for stronger semantics than just a validator.
    """

    default_error_messages = {
        "invalid": _("Please provide a valid date or interval.")
    }

    def __init__(self, formatter=None, format=None, locale=None, **kwargs):
        """Contructor."""
        self.formatter = formatter or LocalizedEDTFFormatter(
            format=format, locale=locale)
        super(LocalizedEDTFDateString, self).__init__(**kwargs)

    def _parse_date_string(self, datestring):
        """Parse input string as EDTF."""
        parser = level0Expression("level0")
        try:
            result = parser.parseString(datestring)
            # check it is chronological if interval
            # NOTE: EDTF Date and Interval both have same interface
            #       and date.lower_strict() <= date.upper_strict() is always
            #       True for a Date
            result = result[0]
            if result.upper_strict() < result.lower_strict():
                raise self.make_error("invalid")
            return result
        except ParseException:
            raise self.make_error("invalid")

    def _serialize(self, value, attr, data, **kwargs):
        """Serialize a Localized EDTF Level 0 formatted date string.

        dump()-equivalent operation.

        NOTE: Level 0 allows for an interval.
        NOTE: ``level0Expression`` tries hard to parse dates. For example,
              ``"2020-01-02garbage"`` will parse to the 2020-01-02 date.
        """
        result = self._parse_date_string(value)
        # Format string
        if self.formatter:
            if isinstance(result, Interval):
                # range value
                result = self.formatter.format_range_date(
                    [result.lower, result.upper])
            else:
                result = self.formatter.format_date(result, strict="lower")
        return (
            super(LocalizedEDTFDateString, self)
            ._serialize(str(result), attr, data, **kwargs)
        )
