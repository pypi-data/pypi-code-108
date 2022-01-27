# -*- coding: utf-8 -*-

"""
This module implements the CloudCIX API JSON Encodes and Decoders, along with other utilities to improve the quality of
life for anyone using the CloudCIX library.
"""

import datetime
import decimal
import json
import re
import uuid
from dateutil import parser

IP_PATTERN = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder that can encode date/time/timedelta, decimal and other python objects into JSON.

    Inspired by Django Rest Framework
    """

    def default(self, obj):
        """
        Converts the passed object into its JSON representation, usually by converting them into a string.

        :param obj: The object to be converted into JSON
        :type obj: object
        """
        if isinstance(obj, datetime.datetime):
            rep = obj.isoformat()
            if rep.endswith('+00:00'):
                rep = rep[:-6] + 'Z'
            return rep
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            # Check to ensure the time isn't timezone aware
            if obj.utcoffset() is not None:
                raise ValueError(
                    'JSON cannot represent timezone-aware times',
                )
            rep = obj.isoformat()
            if obj.microsecond:
                rep = rep[:12]
            return rep
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif hasattr(obj, '__getitem__'):
            try:
                return dict(obj)
            except (KeyError, ValueError):
                pass
        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)
        return super(JSONEncoder, self).default(obj)


class JSONDecoder(json.JSONDecoder):
    """
    JSONDecoder that can decode date/time/timedelta, decimal and other strings into python objects.

    Inspired by Django Rest Framework.
    """

    def __init__(self, *args, **kwargs):
        """
        Create an instance of the Decoder.

        See :py:class:`json.JSONDecoder` for the constructor parameters.
        """
        kwargs.pop('encoding', None)
        super(JSONDecoder, self).__init__(
            *args,
            object_hook=self.parse,
            parse_float=decimal.Decimal,
            **kwargs
        )

    def parse(self, obj):
        """
        Parse a JSON value into its python equivalent.

        If the value is an iterable, this method will be called recursively on every item contained within the value.

        :param obj: The JSON object to be decoded into Python.
        :type obj: Any
        """
        if hasattr(obj, 'items'):
            for k, v in obj.items():
                obj[k] = self.parse(v)
        elif isinstance(obj, str):
            # Check for IP Address separately as it is getting parsed as date
            if IP_PATTERN.match(obj):
                # Skip, we don't want to turn it into a datetime object
                return obj
            try:
                return datetime.datetime.strptime(obj, '%H:%M:%S.%f').time()
            except ValueError:
                pass  # Not a timestamp
            try:
                return datetime.datetime.strptime(obj, '%Y-%m-%d').date()
            except ValueError:
                pass  # Not a date
            try:
                return parser.parse(obj)
            except ValueError:
                pass  # Not a parsable datetime string
        return obj
