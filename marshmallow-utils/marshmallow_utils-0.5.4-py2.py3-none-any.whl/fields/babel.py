# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Localized Extended Date(/Time) Format Level 0 date string field."""

import calendar
from datetime import date, datetime

import arrow
from babel import Locale
from babel.core import negotiate_locale
from babel.dates import LC_TIME, format_date, format_datetime, format_time
from babel_edtf import format_edtf
from marshmallow import fields


class BabelFormatField(fields.String):
    """Base classe for babel date and time formatting fields.

    The babel format field is used only for dumping.
    """

    def __init__(self, format='medium', locale=LC_TIME, parse=True, **kwargs):
        """Constructor.

        :param format: The format to use (either ``short``, ``medium``,
                       ``long`` or ``full``).
        :param locale: The current locale or a callable returning the current
                       locale.
        """
        self._format = format
        self._locale = locale
        self._parse = parse
        kwargs.setdefault('dump_only', True)
        super().__init__(**kwargs)

    @property
    def locale(self):
        """Get the locale to use."""
        return self._locale() if callable(self._locale) else self._locale

    def parse(self, value, as_time=False, as_date=False, as_datetime=False):
        """Parse the value if it's a string."""
        if not self._parse or not isinstance(value, str):
            return value

        a = arrow.get(value)
        if as_time:
            return a.datetime
        elif as_date:
            return a.date()
        elif as_datetime:
            return a.datetime
        else:
            return a

    def format_value(self, value):
        """Format a given value using the chosen format function."""
        raise NotImplementedError()

    def _serialize(self, value, attr, data, **kwargs):
        """Serialize the value."""
        return super()._serialize(
            self.format_value(value), attr, data, **kwargs)


class FormatDate(BabelFormatField):
    """Format a date object."""

    def format_value(self, value):
        """Format an EDTF date."""
        return format_date(
            self.parse(value, as_date=True),
            format=self._format,
            locale=self.locale
        )


class FormatDatetime(BabelFormatField):
    """Format a datetime object."""

    def __init__(self, tzinfo=None, **kwargs):
        """Constructor."""
        self._tzinfo = tzinfo
        super().__init__(**kwargs)

    @property
    def tzinfo(self):
        """Get the timzone to use."""
        return self._tzinfo() if callable(self._tzinfo) else self._tzinfo

    def format_value(self, value):
        """Format an EDTF date."""
        return format_datetime(
            self.parse(value, as_datetime=True),
            format=self._format,
            tzinfo=self.tzinfo,
            locale=self.locale
        )


class FormatTime(FormatDatetime):
    """Format a time object."""

    def format_value(self, value):
        """Format an EDTF date."""
        return format_time(
            self.parse(value, as_time=True),
            format=self._format,
            tzinfo=self.tzinfo,
            locale=self.locale
        )


class FormatEDTF(BabelFormatField):
    """Format an EDTF-formatted string."""

    def format_value(self, value):
        """Format an EDTF date."""
        return format_edtf(value, format=self._format, locale=self.locale)


class BabelGettextDictField(fields.String):
    """Translation string field (dump only).

    This field dumps a translation string as output, by looking up the
    translation in the dictionary provided as input (the message catalog).

    The lookup is performed via babel's locale negotiation (e.g. en_US will
    also match en).

    Basically the fields takes a data object like this::

        {'title': {'en': 'Text', 'da': 'Tekst'}}

    and dumps this (in case the locale is english)::

        {'title': 'Text'}
    """

    default_error_messages = {
        'invalid': 'Not a valid dictionary.',
        'missing_locale': 'Translation not found for ',
    }

    def __init__(self, locale, default_locale, **kwargs):
        """Initialize the field.

        :param locale: The locale to lookup, or a function returning the
            locale.
        :param default_locale: The default locale in case the locale is not
            found. Can be a callable that returns the default locale.
        """
        self._locale = locale
        self._default_locale = default_locale
        kwargs['dump_only'] = True
        super().__init__(**kwargs)

    @property
    def locale(self):
        """Get the locale to be used."""
        return self._locale() if callable(self._locale) else self._locale

    @property
    def default_locale(self):
        """Get the default locale to be used."""
        return self._default_locale() \
            if callable(self._default_locale) else self._default_locale

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize the dict into a string.

        The dict is a message catalog with the keys being locale identifiers
        and the values being the translated string.
        """
        if value is None:
            return None
        if not isinstance(value, dict):
            raise self.make_error('invalid')
        translated_str = gettext_from_dict(
            value, self.locale, self.default_locale)
        if translated_str is None:
            raise self.make_error('missing_locale')
        return super()._serialize(translated_str, attr, obj, **kwargs)


def gettext_from_dict(catalog, locale, default_locale):
    """Get translation string from a dictionary."""
    # First try with negotiate_locale. Negotiate locale will not properly
    # negotiate e.g "en" when the available locales are "en_GB" and "da", even
    # though "en_GB" could be used.
    selected = negotiate_locale([str(locale)], catalog.keys())
    if selected:
        return catalog[selected]

    # In situations where negotiate locale doesn't work, we check if the
    # language itself might be found.

    # Extract language keys only.
    catalog_langs = {
        Locale.parse(l).language: l for (l, msg) in catalog.items()
    }
    if isinstance(locale, str):
        locale = Locale.parse(locale)
    if locale.language in catalog_langs:
        # If primary language match, use that
        catalog_key = catalog_langs[locale.language]
        return catalog[catalog_key]
    # If not, use default locale (must be defined it is defined)
    # "en" is set as fallback lng.
    return catalog.get(str(default_locale), "en")
