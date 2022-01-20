# encoding=utf-8

from collections.abc import Iterable, Sized
from datetime import date, datetime
import json
import re
import warnings

from logbook import Logger

from hansken.util import format_datetime, GeographicLocation, omit_empty, Vector


log = Logger(__name__)


# 'known' default maximum number of clauses in a (boolean) query
DEFAULT_MAX_CLAUSE_COUNT = 1024


# collect the type of a compiled pattern (re.Pattern in 3.7+, a runtime type in Python 3.6)
_Pattern = type(re.compile('.*'))


def _format_value(value):
    """
    Formats a value suitable for Hansken Query Language:

    - date, datetime: ISO 8601
    - GeographicLocation: ISO 6709 string
    - tuple of numbers, length 2: assumed to be latlong, formatted as an
      ISO 6709 string.
    - others: no change
    """
    # order is significant here, date is a datetime but date is allowed without a timezone
    if isinstance(value, datetime):
        return format_datetime(value)
    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, GeographicLocation):
        return str(value)
    if isinstance(value, (tuple, list)) and len(value) == 2 and all(isinstance(part, (float, int)) for part in value):
        return str(GeographicLocation(*value))

    return value


def _flatten(q_type, *queries):
    """
    Yields queries or contained clauses if a query is of type q_type.

    :param q_type: (iterable) type of query to flatten
    :param queries: queries to process
    :return: generator yielding queries
    """
    for q in queries:
        if isinstance(q, q_type):
            # flatten the top level only
            for clause in q:
                yield clause
        else:
            yield q


def _parse_scale(scale):
    """
    Parses a scale string into a scale and base or interval as defined by the
    Facet type of the Hansken search request. Parses a scale such as 'log2',
    'log10' or 'linear@1024'.

    :param scale: a scale string
    :return: (scale, arg)
    """
    base = None
    interval = None
    if scale and scale.startswith('log') and len(scale) > len('log'):
        base = int(scale[len('log'):])
        scale = 'log'
    elif scale and scale.startswith('linear@'):
        interval = int(scale[len('linear@'):])
        scale = 'linear'

    return scale, base, interval


class Query:
    """
    Base class for Hansken query types. Implementations are required to
    implement `.as_dict` for transformation to wire format.
    """

    def as_dict(self):
        """
        Turns this query into a dict as specified by the Hansken Query
        Language Specification.
        """
        raise NotImplementedError()

    def __and__(self, other):
        """
        Binary and operator (``&``) handling, resulting in an `.And` query.
        Resulting query is flattened when one or more operands are already
        `.And` queries.
        """
        if not isinstance(other, Query):
            raise TypeError('right hand operand not Query')

        return And(*_flatten(And, self, other))

    def __or__(self, other):
        """
        Binary or operator (``|``) handling, resulting in an `.Or` query.
        Resulting query is flattened when one or more operands are already
        `.Or` queries.
        """
        if not isinstance(other, Query):
            raise TypeError('right hand operand not Query')

        return Or(*_flatten(Or, self, other))

    def __invert__(self):
        """
        Binary not operator (``~``) handling, resulting in a `.Not` query.
        """
        return Not(self)

    def __str__(self):
        """
        Encodes this query as a JSON string.
        """
        return json.dumps(self.as_dict())


class And(Sized, Iterable, Query):
    """
    Boolean conjunction of multiple queries; traces should match all
    contained queries, for example:

    .. code-block:: python

        And(Term('file.name', 'query.py'),
            Range('data.raw.size', min=512))
    """

    def __init__(self, *queries):
        self.queries = set(queries)

    def as_dict(self):
        return {'and': [query.as_dict() for query in self.queries]}

    def __len__(self):
        return len(self.queries)

    def __iter__(self):
        return iter(self.queries)


class Or(Sized, Iterable, Query):
    """
    Boolean disjunction of multiple queries, traces should match any
    contained query, for example:

    .. code-block:: python

        Or(Term('file.name', 'query.py'),
           Range('data.raw.size', max=1024))
    """

    def __init__(self, *queries):
        self.queries = set(queries)

    def as_dict(self):
        return {'or': [query.as_dict() for query in self.queries]}

    def __len__(self):
        return len(self.queries)

    def __iter__(self):
        return iter(self.queries)


class Not(Query):
    """
    Negates a single query, for example:

    .. code-block:: python

        Not(Term('file.name', 'query.py'))
    """

    def __init__(self, query):
        self.query = query

    def as_dict(self):
        return {'not': self.query.as_dict()}


class Nested(Query):
    """
    Query a field for values matching the results of another query, for example:

    .. code-block:: python

        Nested('data.raw.hash.md5', Term('file.name', 'query.py'))
    """

    def __init__(self, field, query):
        self.field = field
        self.query = query

    def as_dict(self):
        return {'nested': {
            'field': self.field,
            'query': self.query.as_dict()
        }}


class Tracelet(Query):
    """
    Restrict a query for a tracelet type to the same tracelet instance of that
    tracelet type.

    .. code-block:: python

        # find traces containing an entity
        Tracelet('entity')

        # find traces containing an entity that has both:
        # - a value starting with "http://"
        # - a confidence of at least 0.9
        Tracelet('entity', Term('entity.value', 'http://*', full=True) & Range('entity.confidence', min=0.9))

    Note that without the `Tracelet` query, the `Term` and `Range` queries above
    could match different entities, ultimately matching traces that contain
    *any* entity with a value starting with ``http://`` and *any* entity with a
    confidence of at least 0.9 (not necessarily to the same entity).
    """
    def __init__(self, tracelet_type, query=None):
        self.tracelet_type = tracelet_type
        self.query = query

    def as_dict(self):
        return {'hasTracelet': {
            'type': self.tracelet_type,
            # default to an empty dict, translating to an any-query (match any tracelet instance)
            'query': self.query.as_dict() if self.query else {}
        }}


class Trace(Query):
    """
    Restrict a tracelet query to tracelets belonging to traces matching the
    inner query.

    .. code-block:: python

        # match entities of type iban, but only if the trace they belong to is from a specific image
        Term('entity.type', 'iban') & Trace(Term('image', '1234-abcd'))
    """
    def __init__(self, query):
        self.query = query

    def as_dict(self):
        return {'hasTrace': {
            'query': self.query.as_dict()
        }}


class Term(Query):
    """
    Query for the value of single field, for example:

    .. code-block:: python

        # search for files with name "query.py"
        Term('file.name', 'query.py')
        # search for occurrences of the term "query" (in either data or metadata)
        Term('query')
    """

    def __init__(self, field_or_value, value=None, full=False):
        """
        Create a new `.Term` query.

        :param field_or_value: the field to search, or (when *value* is not
            supplied) the search value
        :param value: value to search for (only needed when searching a
            specific field)
        :param full: search the untokenized variant of any string, see
            :ref:`full matches <full_match>`
        """
        # allow first param to be the value, set field to 'text' to request a general term search
        if value is None:
            value = field_or_value
            # full matches won't work on text (which expands to both meta and data)
            field = 'meta' if full else 'text'
        else:
            field = field_or_value

        if isinstance(value, float):
            raise TypeError('float value for Term not supported: {}'.format(value))

        self.field = field
        self.value = value
        self.full = full

    def as_dict(self):
        return {'term': {
            'field': self.field,
            'value': _format_value(self.value),
            'fullMatch': self.full,
        }}


class Regex(Query):
    """
    Query a field for string-values matching a regular expression, for example:

    .. code-block:: python

        # search for replies or forwards
        Regex('email.subject', '(re|fw): .*', full=True)
        # search for bombs, or some curious misspellings
        Regex(re.compile(r'bo[mn]+bs'))

    Either a `str` or a `re.Pattern` object is accepted, of which only the
    ``pattern`` property is used.

    .. note::

        - Regular expressions always match entire terms or (in case of
          ``full=True``) properties, as if the regular expression was anchored
          at both ends, see :ref:`full matches <full_match>`.
        - Not every feature supported by Python's `re` module (like particular
          character classes (``\\s`` / ``\\w``), start/end anchors
          (``^``/``$``), look ahead/behind or non-greedy quantifiers (``??`` /
          ``*?``)) will be supported by Hansken. The use of these is *not*
          validated by ``hansken.py``, but will result in errors when submitted.
        - Regular expressions queries are *always* case insensitive and ignore
          diacritics in values.
    """

    def __init__(self, field_or_pattern, pattern=None, full=False):
        """
        Create a new `.Regex` query.

        :param field_or_pattern: the field to match, or (when *pattern* is not
            supplied) the search pattern
        :param pattern: pattern to match, either a `str` or `re.Pattern`
        :param full: match the untokenized variant of the value, see
            :ref:`full matches <full_match>`
        """
        # allow first param to be the pattern, set field to 'text' to request a general term match
        if pattern is None:
            pattern = field_or_pattern
            # full matches won't work on text (which expands to both meta and data)
            field = 'meta' if full else 'text'
        else:
            field = field_or_pattern

        if isinstance(pattern, _Pattern):
            if pattern.flags & ~re.UNICODE:
                log.warn('regular expression flags in Query objects are ignored ({} used by pattern)',
                         str(re.RegexFlag(pattern.flags)))
            # remote has no use for a Pattern object, use value's original pattern string
            pattern = pattern.pattern

        if not isinstance(pattern, str):
            # the only sanity check we can do on the client side
            raise TypeError(f'query value for Regex must be str, not {type(pattern).__name__}')

        self.field = field
        self.pattern = pattern
        self.full = full

    def as_dict(self):
        return {'regex': {
            'field': self.field,
            'value': self.pattern,
            'fullMatch': self.full,
        }}


class Range(Query):
    """
    Query a field for values in a particular range, for example:

    .. code-block:: python

        # search for traces with entropy between 4.0 (exclusive) and 7.0 (inclusive)
        Range('data.raw.entropy', gt=4.0, max=7)
        # search for traces no larger than 1MiB (1 << 20 == 2 ** 20 == 1048576 bytes)
        Range('data.raw.size', max=1 << 20)
        # search for traces with peculiar names (matches file name aab.txt, but not ccb.txt)
        Range('file.name', min='aa', max='cc')
    """
    _range_keys = {
        'gt': '>',
        'gte': '>=',
        'lt': '<',
        'lte': '<=',
        'max': '<=',
        'maxvalue': '<=',
        'max_value': '<=',
        'min': '>=',
        'minvalue': '>=',
        'min_value': '>=',
    }

    def __init__(self, field, **ranges):
        """
        Create a new `.Range` query.

        :param field: the field to query for
        :param ranges: keyword arguments of the following forms:

            - ``>``, ``gt``: value should be greater than supplied value;
            - ``>=``, ``gte``, ``min``, ``minvalue``, ``min_value``: value should
              be greater or equal to supplied value;
            - ``<``, ``lt``: value should be less than supplied value;
            - ``<=``, ``lte``, ``max``, ``maxvalue``, ``max_value``: value should
              be less or equal to supplied value;
        """
        self.field = field
        # translate kwarg type range to hansken keys
        self.ranges = {self._range_keys.get(key, key): value for key, value in ranges.items()}

        if len(ranges) != len(self.ranges):
            raise ValueError('duplicate mapping in ranges for Range')

    def as_dict(self):
        q = {'field': self.field}
        q.update(self.ranges)

        return {'range': q}


class Exists(Query):
    """
    Search for traces that have a particular field, for example:

    .. code-block:: python

        Exists('email.headers.In-Reply-To')
    """

    def __init__(self, field):
        self.field = field

    def as_dict(self):
        return {'exists': self.field}


class Phrase(Query):
    """
    Search for a phrase of terms, occurring within a particular distance of
    each other, for example:

    .. code-block:: python

        Phrase('email.subject', 'sell you a bomb')
        # will also match "sell you a bomb", not restricted to just email.subject
        Phrase('sell bomb', distance=2)
    """

    def __init__(self, field_or_value, value=None, distance=0):
        """
        Create a new `.Phrase` query.

        :param field_or_value: the field to search, or (when *value* is not
            supplied) the search value
        :param value: value to search for (only needed when searching a
            specific field)
        :param distance: the max number of position displacements between
            terms in the phrase (0 being an exact phrase match)
        """
        # allow first param to be the value, set field to 'text' to request a general phrase search
        if value is None:
            value = field_or_value
            # switch to magical property 'text', expanding to both 'meta' and 'data'
            field = 'text'
        else:
            field = field_or_value

        if len(value) > 1000:
            raise ValueError('value too long for Phrase: {}'.format(len(value)))
        if '?' in value or '*' in value:
            raise ValueError('wildcard in value not allowed for Phrase: {}'.format(value))

        self.field = field
        self.value = value
        self.distance = distance

    def as_dict(self):
        return {'phrase': {
            'field': self.field,
            'value': self.value,
            'distance': self.distance,
        }}


class GeoBox(Query):
    """
    Search for traces with location data within the bounding box between two
    corner points: southwest and northeast, for example:

    .. code-block:: python

        # a location can either be a 2-tuple (…)
        GeoBox('gps.latlong', (-1, -2), (3, 4))
        # (…) or an ISO 6709 latlong string
        GeoBox('gps.latlong', '+12.5281-070.0229', '+13.5281-080.0229')
    """

    def __init__(self, field, southwest, northeast):
        self.field = field
        self.sw = southwest
        self.ne = northeast

    def as_dict(self):
        return {'geobox': {
            'field': self.field,
            'southwest': _format_value(self.sw),
            'northeast': _format_value(self.ne),
        }}


class HQLHuman(Query):
    """
    Search for traces using HQL Human query syntax, for example:

    .. code-block:: python

        HQLHuman('file.name:query.py')
        HQLHuman('data.raw.size>1024')
    """

    def __init__(self, query):
        if not isinstance(query, str):
            raise TypeError('HQL-Human query not a string: {}'.format(query))

        self.query = query

    def as_dict(self):
        return {'human': self.query}


def to_query(query):
    """
    Make sure *query* is a `.Query` instance by either wrapping it with a
    `.HQLHuman` or returning it as is.

    :param query: either a `str` or a `.Query`
    :return: a `.Query` instance
    :raise TypeError: when *query*'s type is not acceptable
    """
    if query is None:
        return None
    if isinstance(query, str):
        return HQLHuman(query)
    if isinstance(query, Query):
        return query

    raise TypeError('query should be either str or hansken.query.Query, not {}'.format(type(query)))


_sort_direction = {
    'ascending': 'ascending',
    'asc': 'ascending',
    '+': 'ascending',
    'descending': 'descending',
    'desc': 'descending',
    '-': 'descending',
}


class Sort:
    def __init__(self, field, direction=None, filter=None, mode=None, value=None):
        """
        Creates a sort clause for use with a search request.

        The *mode* parameter determines what kind of sorting should be applied:

        - ``value``: a regular sort-by-value (the default applied by the
          remote);
        - ``exists``: simply sort on whether the sort field as a value;
        - ``cosineSimilarity``: use parameter *value* to sort on the cosine
          similarity between *value* and the value of the sort field;
        - ``manhattanDistance``: similarly sort on the manhattan distance (or
          L1 norm) between *value* and the value of the sort field;
        - ``euclideanDistance``: similarly sort on the euclidean distance (or
          L2 norm) between *value* and the value of the sort field;

        :param field: the field to sort on
        :param direction: the sorting direction (ascending or descending, or
            ``None`` to auto-determine the sort direction from other arguments)
        :param filter: an optional query to restrict the tracelets included for
                       sorting
        :param mode: a sort mode (see above)
        :param value: a (vector) value to use for similarity / distance
                      calculations in applicable sorting modes (see above)
        """
        self.field = field
        self.filter = filter
        self.mode = mode
        self.value = value

        if isinstance(self.value, Vector):
            # if value is a supplied as a Vector object, coerce it to a str
            # otherwise, leave it as (already a str, None, list of floats, …)
            self.value = str(value)

        if self.value and not self.mode:
            # mode is required when value is supplied
            # default to cosine similarity if user supplied no mode
            self.mode = 'cosineSimilarity'

        if direction:
            # require arg to be known when provided
            self.direction = _sort_direction[direction.lower()]
        else:
            # no explicit direction specified, default to ascending, unless the mode is cosineSimilarity
            # (high similarity score is 'low distance', inverting the intuitive sorting order)
            self.direction = 'descending' if self.mode == 'cosineSimilarity' else 'ascending'

    def as_dict(self):
        return omit_empty({
            'field': self.field,
            'direction': self.direction,
            'filter': to_query(self.filter).as_dict() if self.filter else None,
            'mode': self.mode,
            'value': self.value,
        })

    @classmethod
    def from_str(cls, sort):
        """
        Creates a `.Sort` from *sort*, parsing field, direction and filter.

        Formats supported:

        - ``some.field``: sort on field "some.field", ascending
        - ``some.field+``: sort on field "some.field", ascending
        - ``some.field-``: sort on field "some.field", descending
        - ``some.field | query*``: sort on field "some.field" within matches
          for query "query*", ascending (sorting non-matches after matches)

        :param sort: a sorting string to parse
        :return: a `.Sort` instance
        """
        parts = sort.split('|', 1)

        direction = None
        field = parts[0].strip()
        if field[-1] in ('+', '-'):
            direction = _sort_direction[field[-1]]
            field = field[:-1]

        filter = None
        if len(parts) == 2:
            filter = HQLHuman(parts[1].strip())

        return cls(field, direction, filter)


def to_sort(sort):
    if sort is None:
        return None
    if isinstance(sort, str):
        return Sort.from_str(sort)
    if isinstance(sort, Sort):
        return sort

    raise TypeError('sort should be either str or hansken.query.Sort, not {}'.format(type(sort)))


class Facet:
    def __init__(self, field, size=100, include_total=None, scale=None, filter=None):
        self.field = field
        self.size = size
        self.include_total = include_total
        self.filter = to_query(filter)

        if scale:
            # discourage use of direct Facet with custom parsed scale
            warnings.warn(DeprecationWarning('using scale on Facet is deprecated, use one of the sub types instead'))

        self.scale, self.base, self.interval = _parse_scale(scale)

        self.precision = self.min = self.max = self.sw = self.ne = None

    def as_dict(self):
        """
        Turns this facet into a dict as specified by the Hansken Query
        Language Specification.
        """
        return omit_empty({
            'field': self.field,
            'size': self.size,
            'includeTotal': self.include_total,
            'scale': self.scale,
            'base': self.base,
            'interval': self.interval,
            # make sure to format dates and date(time)s as ISO 8601
            'min': _format_value(self.min),
            'max': _format_value(self.max),
            'precision': self.precision,
            # make sure to format coordinates as ISO 6709
            'southwest': _format_value(self.sw),
            'northeast': _format_value(self.ne),
            'filter': self.filter.as_dict() if isinstance(self.filter, Query) else self.filter
        })

    def __str__(self):
        """
        Encodes this facet as a JSON string.
        """
        return json.dumps(self.as_dict())


class TermFacet(Facet):
    def __init__(self, field, size=100, include_total=None, filter=None):
        """
        Create a new `.TermFacet` to use with a query. A term facet can be
        created on any type of field, counting the occurrences of any value.

        :param field: field to create a facet on
        :param size: the max number of facet counters to return, default is
            100
        :param filter: only count traces matching filter
        """
        super().__init__(field=field, size=size, include_total=include_total, filter=filter)


class RangeFacet(Facet):
    def __init__(self, field, scale, base=None, interval=None, min=None, max=None, include_total=None, filter=None):
        """
        Create a new `.RangeFacet` to use with a query. A range facet can be
        made on either numeric or date fields.

        :param field: field to create a facet on
        :param scale:
            - ``year``, ``month``, ``day``, ``hour``, ``minute`` or ``second``
              for date fields
            - ``linear`` or ``log`` for numeric fields
        :param base: logarithmic base when scale is `'log'`
        :param interval: interval or bucket size when scale is `'linear'`
        :param min: minimum value to include in the facet result
        :param max: maximum value to include in the facet result
        :param filter: only count traces matching filter
        """
        if scale not in ('log', 'linear', 'year', 'month', 'day', 'hour', 'minute', 'second'):
            raise ValueError('unknown scale: {}'.format(scale))

        if scale in ('year', 'month', 'day', 'hour', 'minute', 'second') and (base or interval):
            # date range facet, base and interval are illegal
            raise ValueError('date range facet cannot be combined with base or interval')
        elif scale == 'log' and (not base or interval):
            # numeric log facet, requires base, interval is illegal
            raise ValueError('numeric log facet needs base, cannot be combined with interval')
        elif scale == 'linear' and base:
            # numeric linear facet, base is illegal
            raise ValueError('numeric linear facet cannot be combined with base')

        super().__init__(field=field, include_total=include_total, filter=filter)

        self.scale = scale
        self.base = base
        self.interval = interval
        self.min = min
        self.max = max


class GeohashFacet(Facet):
    def __init__(self, field, size=100, include_total=None, precision=1, southwest=None, northeast=None, filter=None):
        """
        Create a new `.Facet` to use with a query.

        :param field: field to create a facet on
        :param size: the max number of facet counters to return, default is
            100
        :param precision: number of characters of the returned geohashes
        :param southwest: south west bound / corner point
        :param northeast: north west bound / corner point
        :param filter: only count traces matching filter
        """
        bounds = (southwest, northeast)
        if any(bounds) and not all(bounds):
            raise ValueError('specify either both southwest and northeast bounds or neither')

        super().__init__(field=field, size=size, include_total=include_total, filter=filter)

        self.precision = precision
        self.sw = southwest
        self.ne = northeast


def to_facet(facet):
    if facet is None:
        return None
    if isinstance(facet, str):
        return TermFacet(facet)
    if isinstance(facet, Facet):
        return facet

    raise TypeError('facet should be either str or hansken.query.Facet, not {}'.format(type(facet)))
