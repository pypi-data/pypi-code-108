import datetime
import decimal
import json
import uuid
from json import JSONDecodeError, JSONDecoder, load, loads

from .clock import format_iso8601 as _format_iso8601
from .clock import is_timezone_aware as _is_timezone_aware

__all__ = [
    "dump",
    "dumps",
    "load",
    "loads",
    "JSONDecoder",
    "JSONDecodeError",
    "JSONEncoder",
]


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types, and
    UUIDs.

    source: https://github.com/django/django/blob/3.2.11/django/core/serializers/json.py
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            return _format_iso8601(o)
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if _is_timezone_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, (decimal.Decimal, uuid.UUID)):
            return str(o)
        else:
            return super().default(o)


def dumps(obj, ensure_ascii=False, indent=None, **kwargs):
    """
    Serialize ``obj`` to a JSON formatted ``str``.
    """
    return json.dumps(
        obj,
        indent=indent,
        ensure_ascii=ensure_ascii,
        cls=JSONEncoder,
        **kwargs
    )


def dump(obj, fp, ensure_ascii=False, indent=None, **kwargs):
    """
    Serialize ``obj`` as a JSON formatted stream to ``fp`` (a
    ``.write()``-supporting file-like object).
    """
    json.dump(
        obj,
        fp,
        indent=indent,
        ensure_ascii=ensure_ascii,
        cls=JSONEncoder,
        **kwargs
    )
