# encoding=utf-8

from base64 import b64decode as real_b64decode, b64encode as real_b64encode
import binascii
from collections import namedtuple
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from io import RawIOBase
import math
import re
import struct

from ijson import basic_parse as ijson_basic_parse, items as ijson_items, parse as ijson_parse
import iso8601
from logbook import Logger


log = Logger(__name__)


# signal value used when parsing an invalid date
INVALID_DATE = datetime.min.replace(tzinfo=timezone.utc)


# typing is a bit bugged; b64encode uses bytes for both input and output, convert output to str
def b64encode(s):
    """
    Encodes `bytes` to a `str` using default Base64 encoding.

    :param s: `bytes`
    :return: *s*, Base64-encoded
    :rtype: `str`
    """
    return str(real_b64encode(s), 'ascii')


def b64decode(s, validate=False):
    """
    Decode a Base64-encoded string.

    :param s: the string to decode
    :param validate: validate the input against the Base64 alphabet
    :return: decoded byte string
    :rtype: `bytes`
    :raise TypeError: when an invalid character is found
    """
    if not isinstance(s, bytes):
        s = bytes(s, 'ascii')

    try:
        return real_b64decode(s, validate=validate)
    except binascii.Error as e:
        raise TypeError(str(e)) from e


def omit_empty(mapping):
    """
    Filters mapping to a new dict with non-``None`` values.

    :param mapping: dict to filter
    :return: dict containing keys and values from mapping that are non-empty
    """
    return {key: value for key, value in mapping.items() if value is not None}


def glue_url(*path):
    """
    Glues parts of a url path to each other using /s, dropping any steps that
    are None.

    :param path: steps to join
    :return: a url path
    """
    return '/'.join(str(step).strip('/ ') for step in path if step is not None)  # omit steps that are None


def json_events(fd):
    """
    Generates prefixed json parsing events. See also ijson.parse.

    :param fd: file-like object to read from
    :return: an event generator
    """
    return ijson_parse(ijson_basic_parse(fd, use_float=True))


def json_items(events, prefix):
    """
    Generates python values parsed from the provided event stream that
    conform to prefix. See also ijson.items.

    :param events: a json event stream (see json_events)
    :param prefix: prefix of elements to generate (dot-separated, use "item"
                   for array items)
    :return: a value generator
    """
    return ijson_items(events, prefix)


# binary suffixes for byte sizes
_byte_sizes = ('bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB')


def format_byte_size(size, template='{value:.4g} {unit}'):
    """
    Converts a byte size into a human-readable format using binary suffixes.

    :param size: the value to be formatted
    :param template: a format string with two named parameters: *value* and
        *unit*
    :return: a human-readable file size
    """
    # find the order of magnitude (log_2(size) / 10)
    order = int(math.log(size, 2) // 10) if size else 0

    if order >= len(_byte_sizes):
        # exceeding ludicrous file sizes, default to bytes
        return '{} bytes'.format(size)
    # format the template with a human-readable byte size
    return template.format(value=size / (1 << (order * 10)), unit=_byte_sizes[order])


def parse_byte_size(value):
    """
    Turns a human-readable byte size into a numeric value.

    Suffixes are always interpreted as binary and can take a single or triple
    character form (e.g. *m*, *MiB* for megabytes), casing is ignored.

    :param value: a human-readable file size
    :return: an `int`-representation of *value*
    """
    try:
        # match '15', '15k', '15KiB', '1.2 M', …
        match = re.match(r'^(?P<num>(?:\d*\.)?\d+)\s*(?P<suffix>[a-z]*)$', value, re.IGNORECASE)
        num, suffix = match.groups()
        num = float(num)
        # default order 0 (just bytes)
        order = 0
        if suffix:
            # there was a suffix in value, determine the order by looking at the suffix' index in _byte_sizes
            order = next((i for i, size in enumerate(_byte_sizes) if size.lower().startswith(suffix.lower())))

        # calculate the byte size as the product of the supplied value and the binary order multiplier
        return round(num * (1 << (order * 10)))
    except Exception as e:
        # any exception (when match of next fails, for example) result in an invalid byte size error
        raise ValueError('invalid byte size: {}'.format(value)) from e


def format_datetime(ts):
    """
    Coverts a `datetime.datetime` object into ISO-8601 wire format, while
    requiring a timezone.

    :param ts: the `datetime` to be converted
    :return: *ts*, in ISO-8601 format
    """
    if not ts.tzinfo:
        raise ValueError('datetime without timezone')

    return ts.isoformat()


def parse_datetime(value):
    """
    Parses an ISO8601-formatted timestamp into a `datetime` object.

    Returns `.INVALID_DATE` when an invalid value is passed (e.g. a negative
    year component, which is not supported by `datetime`).

    :param value: an ISO8601-formatted `str`
    :return: a `datetime` object representing the same value as *value*
    """
    try:
        return iso8601.parse_date(value)
    except iso8601.ParseError:
        # NB: value "-1234-01-21…" would technically be valid in ISO 8601, though Python's datetime does not allow it
        log.warning('failed to parse {} as datetime, defaulting to {}', value, INVALID_DATE, exc_info=True)
        return INVALID_DATE


class GeographicLocation(namedtuple('GeographicLocation', ('latitude', 'longitude'))):
    """
    Describes a 2-tuple *(latitude, longitude)* to translate location data to
    and from Hansken's wire format.
    """

    _pattern = re.compile(r'^(?P<latitude>[+\-]?\d+\.\d+)(?P<longitude>[+\-]?\d+.\d+)/?$')

    @classmethod
    def from_string(cls, value):
        """
        Parses a string value into a `GeographicLocation`.

        :param value: a string-representation to be parsed
        :return: a value of type `cls`, parsed from *value*
        """
        match = cls._pattern.match(value)
        if not match:
            raise TypeError('invalid {cls.__name__}: {value}'.format(cls=cls, value=value))

        # use keyword arguments to instantiate cls (extensions beware :))
        return cls(latitude=float(match.group('latitude')), longitude=float(match.group('longitude')))

    def __str__(self):
        # use zero-padded floating point values with forced sign rounded to a 5 digit fraction
        return '{location.latitude:+09.5f}{location.longitude:+010.5f}'.format(location=self)


class Vector(Sequence):
    """
    Describes a sequence of floating point numbers to translate vector data to
    and from Hansken's wire format.
    """

    # compile a struct for values in a Vector: big-endian 32 bit float
    _struct = struct.Struct('>f')

    @classmethod
    def from_base64(cls, value):
        """
        Creates a `.Vector` from *value*, assuming it will be base64-encoded
        sequence of big-endian 4-byte IEEE-754 floating points.

        :param value: a base64-representation to be parsed
        :return: a new `.Vector`
        """
        return cls(b64decode(value))

    @classmethod
    def from_sequence(cls, seq):
        """
        Creates a `.Vector` from *seq*, assuming it will be a sequence of
        elements compatible with the ``f`` struct format character.

        :param seq: a sequence of `float`
        :return: a new `.Vector`
        """
        size = cls._struct.size
        # allocate a buffer that would fit the entire sequence
        buffer = bytearray(len(seq) * size)
        for idx, element in enumerate(seq):
            # pack all elements into the pre-allocated buffer
            cls._struct.pack_into(buffer, idx * size, element)

        # wrap buffer into bytes to make sure the result's _raw attribute is a bytes (required by __bytes__)
        return cls(bytes(buffer))

    def __init__(self, data):
        """
        Creates a new `.Vector` backed by the provided data.

        :param data: a byte buffer, aligned to 4 bytes
        """
        if len(data) % self._struct.size:
            raise TypeError(f'misaligned data, {len(data)} not a multiple of {self._struct.size}')

        self._raw = data

    def __len__(self):
        return len(self._raw) // self._struct.size

    def __getitem__(self, item):
        size = self._struct.size

        if isinstance(item, slice):
            # or self[idx], but bypass a bunch of type and size checks
            return [self._struct.unpack_from(self._raw, offset=idx * size)[0]
                    # let range and slice generate the actual indices we need
                    for idx in range(*item.indices(len(self)))]

        if not isinstance(item, int):
            # mimic the error list would create
            raise TypeError(f'indices should integers or slices, not {item.__class__.__name__}')

        if item >= len(self):
            # we're responsible for this check (__iter__ relies on this behaviour)
            raise IndexError

        # unpack a single value from the underlying buffer
        # (unpack always returns a tuple, we always need the first and only element)
        return self._struct.unpack_from(self._raw, offset=item * size)[0]

    def __bytes__(self):
        return self._raw

    def __str__(self):
        return b64encode(bytes(self))

    def __repr__(self):
        return f'{self.__class__.__name__}({list(self)})'


class MultiContext:
    """
    Context manager delegating its `__enter__` and `__exit__` methods to the
    provided set of context managers.

    `__enter__` is called on all delegates in the order they've been supplied.
    `Exception` s raised from these calls are collected, if any of the
    delegates raised an `Exception`, a `ValueError` is raised with an error
    message and the recorded `Exception` instances. `__exit__` is *not* called
    in this case.

    `__exit__` is called on all delegates in the the reverse order they've been
    supplied. The exception detail arguments for `__exit__` are passed to the
    delegates verbatim. The return value for `__exit__` will be truthy if any
    of the delegate calls return a truthy value (which would cause the
    interpreter to suppress the error.

    Any delegates raising an `Exception` of their own on `__exit__` produce
    undefined behaviour; errors on `__exit__` should be avoided.

    Use `.MultiContext` as a context manager:

    .. code-block:: python

        with MultiContext(manager1, manager2):
            do_things()

        # note that this is equivalent to
        with manager1, manager2:
            do_things()

        # MultiContext can be used as a return type for multiple context managers
        with create_context_managers():
            do_things()
    """

    def __init__(self, *contexts):
        """
        Creates a new `.MultiContext`, delegating its `__enter__` and
        `__exit__` calls to the provided delegate context managers.

        :param contexts: delegate context managers
        """
        self.contexts = contexts

    def __enter__(self):
        errors = []

        for context in self.contexts:
            try:
                context.__enter__()
            except Exception as e:
                # warn here to indicate which context failed to enter
                log.warn('context {} failed to __enter__', context, e)
                errors.append(e)

        if errors:
            # don't silence errors
            raise ValueError('failed to __enter__ MultiContext', *errors)

        # always return self to make sure self.__exit__ is called
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # default to falsy return value
        suppress = False

        for context in reversed(self.contexts):
            # allow short circuiting the or, but make sure delegate.__exit__ is called
            suppress = context.__exit__(exc_type, exc_val, exc_tb) or suppress

        return suppress


class Namespace:
    """
    Utility class to create a tiny namespace with some simple attributes.
    """

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def extend(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)


class DictView(Mapping):
    """
    Dict-like class with separator-aware value retrieval. A dot (.) is used as
    the default separator. Values can be retrieved in one of three methods
    (the first two of which are like a normal dict):

    - calling get: view.get('some.property')
    - indexing: view['some.property']
    - attribute access: view.some.property

    If the retrieved property is a dict, it is wrapped in a DictView to enable
    further DictView access methods.
    """

    # sentinel value used to check when a KeyError should be raised rather than returning a value
    _no_default = object()

    def __init__(self, source, separator='.'):
        self._source = source
        self._separator = separator

    def get(self, key, default=None):
        try:
            value = self._source
            for step in key.split(self._separator):
                value = value[step]

            if isinstance(value, dict):
                return DictView(value)
            else:
                return value
        except KeyError:
            return default

    def __len__(self):
        return len(self._source)

    def __iter__(self):
        return iter(self._source)

    def __contains__(self, item):
        return self.get(item) is not None

    def __getitem__(self, item):
        value = self.get(item, self._no_default)
        if value is self._no_default:
            raise KeyError(item)
        else:
            return value

    def __str__(self):
        return str(self._source)


def view_with_attrs(name=None, attrs=()):  # default attrs to an empty tuple (no attributes)
    """
    Creates a class definition that is an extension of DictView. Attribute
    names are cached and used to lazily get them (either as their original
    name or the PEP8-style equivalent) from the instance's source when
    accessed using __getattr__. For use in interactive shells, __dir__
    includes the named attributes translated to PEP8-style names.

    :param name: name of the generated view class
    :param attrs: attributes to be defined for the requested class
    :return: extension of DictView that loads attributes from the provided
        source dict, renamed to python's conventions
    """

    # transform a sequence of attribute names to a mapping of {name: factory}
    # factory None will not touch the value
    if not isinstance(attrs, Mapping):
        attrs = {attr: None for attr in attrs}

    def to_value(value, name):
        if value is None:
            # avoid handing factories None, None is identical to 'not set'
            return value

        factory = attrs.get(name)
        # let factory transform the value if available
        return factory(value) if factory else value

    class AttrView(DictView):
        def __init__(self, source):
            super().__init__(source)

        def __getattr__(self, item):
            if item in attrs:
                # attribute is defined, fetch from parent
                return to_value(self.get(item), item)

            prop = to_property_name(item)
            if prop in attrs:
                # translated attribute is defined, fetch the translation from parent
                return to_value(self.get(prop), prop)

            # no such attribute
            raise AttributeError(item)

        def __dir__(self):
            base = set(super().__dir__())
            # extend the set of attrs reported up the mro with those explicitly defined for this AttrView
            # NB: the result of dir()/__dir__ is not guaranteed to be 'correct', it is meant for interactive inspection
            return sorted(base | {to_attr_name(attr) for attr in attrs})

    if name is not None:
        AttrView.__name__ = name

    return AttrView


def to_property_name(name):
    """
    Converts a name to a property name by convention (*camelCase*) by
    converting *snake_case* to *snakeCase*.

    :param name: name to convert
    :return: *name* converted to a property name
    """
    return re.sub(r'_[a-z]', lambda match: match.group()[1].upper(), name)


def to_attr_name(name):
    """
    Converts a name to an attribute name by convention (*snake_case*) by
    converting *camelCase* to *camel_case*.

    :param name: name to convert
    :return: *name* converted to a attribute name
    """
    return re.sub(r'[a-z][A-Z]', lambda match: '_'.join(match.group().lower()), name).lower()


def to_class_name(name):
    """
    Converts a name to a class name by convention (*PascalCase*) by converting
    *snake_case* to *SnakeCase*.

    :param name: name to convert
    :return: *name* converted to a class name
    """
    name = re.sub(r'_[A-z]', lambda match: match.group()[1].upper(), name)
    return name[0].upper() + name[1:]


class ChunkedIO(RawIOBase):
    """
    Turns a generator of chunks into raw I/O, which can in turn be fed to
    something like an `io.BufferedReader`.

    .. code-block:: python

        # requesting an imaginary big file, to be sent chunked
        response = requests.get('http://big-files.net/big-file.bin',
                                stream=True)  # make sure to request a stream
        # using 8KiB bytes chunk size, turn the response into a BufferedReader
        reader = io.BufferedReader(
            ChunkedResponseIO(response.iter_content(8192))
        )
    """

    def __init__(self, chunks):
        """
        Creates a `.ChunkedIO`, reading chunks of `bytes` from *chunks*.

        .. note::

            `.ChunkedIO` does no type checking on *chunks* or the chunks it
            yields; only `bytes` chunks will likely work as expected.

        :param chunks: an iterable yielding `bytes`
        """
        self._chunks = chunks
        self._current = None

    def seekable(self):
        return False

    def readable(self):
        return True

    def writable(self):
        return False

    def readinto(self, b):
        if self.closed:
            return 0

        max_read = len(b)
        num_read = 0

        try:
            # reuse current (partial) chunk or use the next chunk if the current one is None or empty
            self._current = self._current or next(self._chunks)
            # keep reading till num_read reaches max_read
            while num_read < max_read:
                # split current chunk into a buffer to be used right now and one for the next call
                buf, self._current = self._current[:max_read - num_read], self._current[max_read - num_read:]
                # put the data to be used now into b
                b[num_read:num_read + len(buf)] = buf
                num_read += len(buf)
                # reuse current (partial) chunk or use the next chunk if the current one is None or empty
                self._current = self._current or next(self._chunks)
        except StopIteration:
            # self._chunks is exhausted, mark self._current as invalid
            self._current = None

        return num_read

    def close(self):
        self._chunks.close()
        super().close()


def flatten_mapping(mapping, separator='.', prefix=None):
    """
    Flattens *mapping* into a single level `dict` by concatenating nested keys.

    :param mapping: the mapping to be flattened
    :param separator: separator to be used to concatenate nested keys
    :param prefix: prefix for all keys in the nested result (typically only
        useful for recursive calls)
    :return: *mapping*, flattened into a single level `dict`
    """
    # collect dict items (tuples) in a list
    items = []

    for key, value in mapping.items():
        if prefix:
            # update the key to be used if there's a prefix
            key = separator.join((prefix, key))

        try:
            # attempt recursive flattening (…)
            items.extend(flatten_mapping(value, prefix=key).items())
        except AttributeError:
            # (…) not a mapping, apparently, just track this item
            items.append((key, value))

    # return a flattened version of mapping
    return dict(items)
