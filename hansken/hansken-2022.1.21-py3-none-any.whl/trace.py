# encoding=utf-8

from collections import namedtuple
from collections.abc import Mapping
from enum import Enum, unique
from itertools import chain
import json
import warnings

from logbook import Logger

from hansken import fetch
from hansken.abstract_trace import AbstractTrace
from hansken.query import Term, to_query
from hansken.util import (b64decode, b64encode,
                          DictView, flatten_mapping,
                          format_datetime, GeographicLocation, parse_datetime,
                          to_attr_name, Vector, view_with_attrs)


log = Logger(__name__)


_converter = namedtuple('_converter', ('serialize', 'deserialize'))


# collection of wire / python type converters by model type
CONVERTERS = {
    # convert binary to / from base64
    'binary': _converter(
        b64encode,
        b64decode,
    ),
    # convert dates to / from datetime.datetime objects (*requiring* a timezone)
    'date': _converter(
        format_datetime,
        parse_datetime,
    ),
    # convert latLong to / from GeographicLocation
    'latLong': _converter(
        str,  # trust we'll hit GeographicLocation.__str__ or coerce a str to itself
        GeographicLocation.from_string,
    ),
    # convert vector to / from Vector
    'vector': _converter(
        str,  # trust we'll hit Vector.__str__ or coerce a str to itself
        Vector.from_base64,
    ),
}


def image_from(trace_uid):
    warnings.warn('image_from is deprecated, use image_from_uid', DeprecationWarning)
    return image_from_uid(trace_uid)


def image_from_uid(trace_uid):
    """
    Splits *trace_uid* into its two parts, *image* and *id*, returning the
    first.
    Note that a `.Trace` object will provide these as properties `image_id` and
    `id`.

    :param str trace_uid: an image uid
    :return: the image UUID from *trace_uid*
    :rtype: `str`
    """
    return trace_uid.split(':', 1)[0]


def image_from_trace(trace):
    """
    Attempts to get an image id from *trace*, whether *trace* is a `.Trace`
    object or `dict`-like.

    :param trace: a `.Trace` or `dict`-like trace
    :return: the image UUID from *trace*
    :rtype: `str`
    """
    if hasattr(trace, 'image_id'):
        return trace.image_id
    if 'image' in trace:
        return trace.get('image')
    if 'uid' in trace:
        return image_from_uid(trace.get('uid'))

    raise ValueError('unable to get image id from trace {}'.format(trace))


@unique
class Privileged(Enum):
    """
    Possible privileged states of a `.Trace`. Values that correspond to 'not
    privileged' (`None` or `.rejected`) are falsy, making them suitable to
    check whether a trace is privileged.
    """

    suspected = 'suspected'  #: trace is suspected of being privileged
    confirmed = 'confirmed'  #: trace is confirmed to be privileged
    rejected = 'rejected'  #: trace is confirmed to be *not* privileged

    def __bool__(self):
        # rejected value should be falsy (see class doc)
        return self is not Privileged.rejected

    def __eq__(self, other):
        if isinstance(other, str):
            # enable comparisons with str values
            return str(self) == other

        return super().__eq__(other)

    def __str__(self):
        return self.value


class Snippet(DictView):
    """
    Snippet result, enabling rendering of a highlighted snippet of text
    content. Usable as a dictionary where key ``'content'`` contains a snippet
    of text and key ``'highlights'`` contains a list of dictionaries encoding
    highlighted terms in the content.
    """

    def render(self, start='[[', end=']]'):
        """
        Render this snippet by surrounding highlights with *start* and *end*
        marker strings, e.g.:

        .. code-block:: python

            >>> my_snippet.render()
            'A [[snippet]] with the term "[[snippet]]" highlighted.'
            >>> my_snippet.render(start='<em>', end='</em>')
            'A <em>snippet</em> with the term "<em>snippet</em>" highlighted.'

        :param start: start marker around highlights
        :param end: end marker around highlights
        :return: this `.Snippet`, highlighted as a `str`
        """
        content = self.get('content')
        highlights = self.get('highlights')

        # gather chunks of text to be joined together later
        chunks = []

        # start at text offset 0
        prev_end = hl_end = 0
        for highlight in highlights:
            hl_start, hl_end = highlight['start'], highlight['end']

            # for each highlight, add content from last highlight up to current start (…)
            chunks.append(content[prev_end:hl_start])
            # (…) then a highlight start marker (…)
            chunks.append(start)
            # (…) followed by the actual highlight content (…)
            chunks.append(content[hl_start:hl_end])
            # (…) and a highlight end marker
            chunks.append(end)

            prev_end = hl_end

        # add a final chunk from the end of the last highlight to the end of the content string
        chunks.append(content[hl_end:])

        return ''.join(chunks)

    def __str__(self):
        return self.get('content')


class Trace(AbstractTrace):
    """
    Base class for traces. Defines convenience methods to navigate or
    manipulate a trace. Trace data may be accessed using `open <.Trace.open>`.
    """

    # value separating sequence numbers in trace ids (e.g. 0-1-23)
    ID_SEP = '-'
    # signal value for lazy post-init values
    _UNINITIALIZED = object()

    def __init__(self, source, context=None):
        super().__init__(source)

        # a super will likely also set these attributes, but we need these for operation without any super classes
        # retrieve the values from source as we're only interested in intrinsics, self.get() inspects the trace model
        self.image_id = source.get('image')  # this will get an intrinsic property, leaving the image type as member
        self.id = source.get('id')
        self.uid = source.get('uid')
        self.name = source.get('name')
        # set parent identifiers if applicable (id/uid might not be available or trace is a root)
        self.parent_id = self.id[:self.id.rindex(Trace.ID_SEP)] if self.id and Trace.ID_SEP in self.id else None
        self.parent_uid = self.uid[:self.uid.rindex(Trace.ID_SEP)] if self.uid and Trace.ID_SEP in self.uid else None
        # default to an empty set, 'type' in trace.types should be possible
        # note that a modeled trace class below would override this
        self.types = self.get('types', set())

        self._tags = None
        self._notes = None
        self._privileged = Trace._UNINITIALIZED  # None is a valid value, use signal value
        self._audits = None

        self._context = context
        self._project_id = context.project_id if context else None

    @property
    def context(self):
        """
        The `ProjectContext <hansken.remote.ProjectContext>` instance that
        created this `.Trace`.
        """
        if self._context:
            return self._context
        else:
            raise ValueError('project context for trace {} not set'.format(self.uid))

    @property
    def image_name(self):
        """
        The name / description of this `.Trace`'s ``image_id``, or ``None``.
        """
        return self.context.image_name(self.image_id) if self.image_id else None

    @property
    def parent(self):
        """
        This `.Trace`' parent `.Trace`, or ``None`` if not applicable.
        """
        return self.context.trace(self.parent_uid) if self.parent_uid else None

    def note(self, note, refresh=None):
        """
        Add a note to this `.Trace`.

        :param str note: the note itself
        :param refresh: if `True`, force a full project refresh, making this
                        note immediately searchable
        """
        self.context.note(self.uid, note, refresh=refresh)

    @property
    def notes(self):
        """
        The notes attached to this `.Trace`. Note that this does not include
        notes added by `note <.Trace.note>`.
        """
        if self._notes is None:
            # TODO: wrap with something that allows to delete a note (HANSKEN-2247)
            self._notes = self.get('user.annotated.#note') or ()

        return self._notes

    def tag(self, tag, refresh=None):
        """
        Tag this trace.

        :param str tag: the tag to set
        :param refresh: if `True`, force a full project refresh, making this
                        note immediately searchable
        """
        self.context.tag(self.uid, tag, refresh=refresh)

    @property
    def tags(self):
        """
        The tags attached to this `.Trace`. Note that this does not include
        tags added by `tag <.Trace.tag>`.
        """
        if self._tags is None:
            # TODO: wrap with something that allows to delete a tag (HANSKEN-2247)
            self._tags = self.get('user.annotated.tags') or ()

        return self._tags

    @property
    def privileged(self):
        """
        The privileged state of this trace, either `None` or one of
        `.Privileged`. Note that `None` is not a valid value when *setting*
        the `.privileged` attribute, an operation that requires authorization.
        """
        if self._privileged is Trace._UNINITIALIZED:
            self._privileged = self.get('user.annotated.privileged', None)

            if self._privileged:
                # value has been set, turn it into a Privileged
                try:
                    self._privileged = Privileged(self._privileged)
                except ValueError as e:
                    # 'reset' the attribute as if freshly constructed
                    self._privileged = Trace._UNINITIALIZED
                    raise ValueError(
                        'unknown privileged state: {}'.format(self.get('user.annotated.privileged'))
                    ) from e

        return self._privileged

    @privileged.setter
    def privileged(self, status):
        status = Privileged(status)
        self.context.mark_privileged(self.uid, status)
        self._privileged = status

    @property
    def creator(self):
        """
        The tool that created this `.Trace`, or ``None`` if unknown. Includes
        the version of that tool, e.g.: ``toolname 1.2.3``.

        .. note::
            This value is formatted by ``hansken.py``, it is not suitable for
            use with queries (like finding other traces created by the same
            tool).
        """
        # attempt to retrieve new-style creator metadata, fall back to old-style metadata
        tool = self.get('system.processed.origin.createdBy') or self.get('system.processed.tool.meta.creator')
        if tool:
            # provide the creator of this trace including its version
            return '{} {}'.format(tool, self.tool_versions.get(tool) or '(unknown version)')

    @property
    def tool_versions(self):
        """
        The tools and versions that are responsible for this `.Trace`'s
        metadata, as a `dict` mapping the names of tools to their respective
        versions. Tool versions typically include the versions of critical
        software libraries used by those tools.
        """
        # attempt to retrieve new-style tool information
        toolruns = self.get('system.processed.toolrun')
        if toolruns:
            # property should be returning {tool name: tool version}, take version from last occurrence
            return {run.get('tool'): run.get('version') for run in toolruns}

        # fall back to old tool metadata (but never None)
        return self.get('system.processed.tool.meta.version') or {}

    @property
    def audits(self):
        """
        An audit log of user-initiated changes to this `.Trace` in the form of
        a sequence of `dict`s, ordered by the audit's creation timestamp. The
        audit log can be empty, but never `None`.
        """
        if self._audits is None:
            # default to empty sequence
            self._audits = self.get('system.processed.audit') or ()
            # createdOn should always be set, but don't crash when it's not available
            # TODO: lexicographic ordering only works when timestamps are in the same timezone (HANSKENPY-177)
            self._audits = sorted(self._audits, key=lambda audit: audit.get('createdOn') or '')

        return self._audits

    def tracelets(self, tracelet_type, query=None, sort=None):
        """
        Provides or retrieves tracelets of type *type*.

        The exact return type of a call to `.tracelets` depends on the tracelet
        type being requested. If the remote defines *type* to be 'few', the
        result will be a `list` of `.Tracelet` objects. If the remote defines
        *type* to be 'many', the result will be a `.SearchResult` of `.Tracelet`
        objects. Note that *query* can only be used with the latter.

        :param tracelet_type: the tracelet type to request
        :param query: query to match tracelets to
        :param sort: ordering of tracelets
        :return: a sized iterable of `.Tracelet` s (iterable once)
        """
        trace_uid_query = Term('traceUid', self.uid)
        # ensure we're searching for tracelets belonging to this trace
        query = to_query(query) & trace_uid_query if query else trace_uid_query
        return self.context.search_tracelets(tracelet_type, query=query, sort=sort)

    @property
    def children(self):
        """
        A `SearchResult <hansken.remote.SearchResult>` instance containing the
        child traces of this `.Trace`, if any.
        """
        return self.context.children(self.uid)

    @property
    def data_types(self):
        """
        A set of data type names available for this `.Trace`. These names can
        be used with calls to `open <.Trace.open>` or attribute access like

        .. code-block:: python

            if 'raw' in trace.data_types:
                # trace has a raw data stream, attribute access to data.raw.size will be safe
                print('raw data size:', trace.data.raw.size)

            for data_type in trace.data_types:
                # format a file name as the trace's name, using the data type name as the extension
                # (e.g. "some-file.raw" or "another-file.text")
                out_file = '{}.{}'.format(trace.name, data_type)
                print('writing first 64 bytes to', out_file)
                with open(out_file, 'wb') as out_file:
                    # out_file now opened for writing in binary mode
                    # write the first 64 bytes of trace's stream of type data_type to the file
                    out_file.write(trace.open(data_type, size=64).read())

        :return: data type names available for this `.Trace` (possibly empty,
            but never `None`)
        :rtype: `set`
        """
        if hasattr(self, 'data'):
            # likely a modeled trace
            return set(self.data.keys())

        # get a view on the extracted data type (possibly empty or None) (…)
        data = self.get('system.extracted.data')
        # (…) and always return a set
        return set(data.keys() if data else [])

    def open(self, stream='raw', offset=0, size=None, key=fetch):
        """
        Open a data stream of a named stream (default ``raw``) for this
        `.Trace`.

        .. note::
            Multiple calls to `read(num_bytes)` on the stream resulting from
            this call works fine in Python 3, but will fail in Python 2.

        :param stream: stream to read
        :param offset: byte offset to start the stream on
        :param size: the number of bytes to make available
        :param key: key for the image of this trace (default is to fetch the
            key automatically, if it's available)
        :return: a file-like object to read bytes from the named stream
        :rtype: `io.BufferedReader`
        """
        return self.context.data(self.uid, stream, offset, size, key)

    @property
    def preview_types(self):
        """
        A set of preview type names (mime types) available for this `.Trace`.
        These names can be used with calls to `preview <.Trace.preview>`.

        :return: preview type names available for this `.Trace` (possibly
            empty, but never `None`)
        :rtype: `set`
        """
        previews = self.get('previews')
        return set(previews.keys() if previews else [])

    def preview(self, mime_type):
        """
        Gets a preview of a particular mime type, e.g. 'text/plain' or
        'image/png'.

        :param mime_type: the preview type to get
        :return: `bytes` or `None`
        """
        previews = self.get('previews')
        if previews and mime_type in previews:
            return b64decode(previews.get(mime_type))
        else:
            # no previews or no such mime type in previews
            return None

    def snippets(self, query, num=100, before=200, after=200):
        """
        Generate snippets surrounding term hits from *query* in any of the
        data streams of this trace.

        :param query: the query to generate snippets for (should contain term
            queries, or no snippets will be generated)
        :param num: maximum number of snippets to return
        :param before: number of bytes to include before the term hits
        :param after: number of bytes to include after the term hits
        :return: `list` of `.Snippet` instances
        """
        with self.context.search(query=Term('uid', self.uid) & to_query(query), count=1, snippets=num) as result:
            snippets = result.takeone(include='snippets')
            if snippets:
                # takeone() is safe, unpacking a potential None is not
                _, snippets = snippets
            if not snippets:
                # either no results or no snippets for the only result
                return []

            # gather unique terms from al of the generated snippets
            terms = list({snippet['term'] for snippet in snippets})
            image_key = self.context.key(self.image_id)
            image_key = b64encode(image_key) if image_key else None
            if hasattr(self, 'data'):
                # likely a modeled trace, let get() deal with data origins and categories
                data_sizes = {data_type: self.get('data.{}.size'.format(data_type))
                              for data_type in self.data_types}
            else:
                # plain trace, assume data property path to be in origin system
                data_sizes = {data_type: self.get('system.extracted.data.{}.size'.format(data_type))
                              for data_type in self.data_types}
            # transform all the snippets into snippet requests, using all the returned terms for each request
            snippets = [
                {'uid': self.uid,
                 'imageKey': image_key,
                 'dataType': snippet['dataType'],
                 'highlights': terms,
                 # request data from *around* the term hit
                 # offset parameters are validated, clip to stream bounds
                 'start': max(0, snippet['start'] - before),
                 'end': min(snippet['end'] + after, data_sizes[snippet['dataType']])}
                for snippet in snippets
            ]

            return self.context.snippets(*snippets)

    def update(self, key_or_updates=None, value=None, data=None, overwrite=False):
        """
        Requests the remote to update or add metadata properties for this
        `.Trace`.

        .. note::

            Calls to `update` will *not* update the source of the `.Trace`
            it's being called on. To get a `.Trace` instance including the
            changes made after a successful call to `update`, use
            ``trace.context.trace(trace.uid)`` to request a new instance of
            a trace with this `.Trace`'s identifier.

        :param key_or_updates: either a `str` (the metadata property to be
            updated) or a mapping supplying both keys and values to be updated
            (or `None` if only data is supplied)
        :param value: the value to update metadata property *key* to (used
            only when *key_or_updates* is a `str`)
        :param data: a `dict` mapping data type / stream name to bytes to be
            imported
        :param overwrite: whether properties to be imported should be
            overwritten if already present
        :return: processing information from remote
        """
        updates = key_or_updates
        if isinstance(key_or_updates, str):
            updates = {key_or_updates: value}

        return self.context.update_trace(self, updates, data=data, overwrite=overwrite)

    def child_builder(self, name=None):
        """
        Create a `.TraceBuilder` to build a trace to be saved as a child of
        this `.Trace`. Note that ``name`` is a mandatory property for a trace,
        even though it is optional here. A ``name`` can be added later using
        the `.TraceBuilder.update` method. Furthermore, a new trace will only
        be added to the index once explicitly saved (e.g. through
        `.TraceBuilder.build`).

        :param name: the name for the trace being built
        :return: a `.TraceBuilder` set up to create a child trace of this
            `.Trace`
        """
        builder = self.context.child_builder(self.uid)

        if name:
            # optionally add a name for the new child trace
            builder.update('name', name)

        return builder

    def __repr__(self):
        return '<{0.__class__.__module__}.{0.__class__.__name__} {0.uid} ({0.name})>'.format(self)


class IncompleteTracePropertyError(ValueError):
    """
    A `ValueError` raised when a trace property is missing required parts.
    """
    pass


class TraceModel(DictView):
    """
    Utility to deal with intricacies surrounding the trace / data model used
    by Hansken. Used by ``hansken.py`` to translate and validate
    user-specified metadata properties to their corresponding place in the
    data structure for a trace in Hansken.
    """

    def __init__(self, source):
        super().__init__(source)

        self._intrinsics = set(self.get('properties', default=[]))
        self._origins = tuple(sorted(self.get('origins.keys', default={}).keys()))
        # create a mapping tracking the category of a type, for efficiency later
        self._categorized_types = {type_name: category_name
                                   for category_name, category in self.get('origins.categories').items()
                                   for type_name in category.get('types', default={}).keys()}
        self._categorized_properties = {property_name: category_name
                                        for category_name, category in self.get('origins.categories').items()
                                        for property_name in category.get('properties', default={}).keys()}
        # NB: it's possible that there's categories without defined types, _categorized_types.values() would skip those
        self._categories = set(self.get('origins.categories', default={}).keys())
        self._types = set(self._categorized_types.keys())
        # create a mapping tracking the data types for mapped types
        self._mapped_types = {type_name: set(type_details.get('keys'))
                              for category_name, category in self.get('origins.categories').items()
                              for type_name, type_details in category.get('types', default={}).items()
                              # type is mapped if its 'keys' property is non-empty
                              if type_details.get('keys')}
        self._data_types = set(self.get('origins.categories.extracted.types.data.keys', []))

    @property
    def intrinsics(self):
        """
        The intrinsic properties (properties that any trace can have,
        regardless of its type(s)) defined by the trace model.
        """
        return self._intrinsics

    def is_intrinsic(self, steps):
        """
        Checks whether the property defined by *steps* is an intrinsic
        property.

        :param steps: steps through a `.Trace`' data structure
        :return: whether the property defined by *steps* is an intrinsic
            property
        """
        return steps[0] in self.intrinsics

    @property
    def origins(self):
        """
        The origins defined by the trace model, typically *system* and *user*.
        """
        return self._origins

    @property
    def categories(self):
        """
        The categories of types and properties defined by the trace model,
        e.g. *extracted* or *annotated*.
        """
        return self._categories

    @property
    def types(self):
        """
        The trace types defined by the trace model, e.g. *file* or
        *classification*.
        """
        return self._types

    @property
    def data_types(self):
        """
        Data named data types defined by the trace model for the "data" trace
        type.
        """
        return self._data_types

    def _expand_from_type(self, category, type_name, rest):
        # category and type name are already provided, lead with those
        yield category
        yield type_name

        try:
            data_types = self._mapped_types.get(type_name, set())
            if data_types:
                # mapped type, verify the data type is valid for the type (e.g. data.raw)
                data_type = next(rest)
                if data_type in data_types:
                    yield data_type
                else:
                    raise KeyError('unknown data type "{}" for trace type "{}"'.format(data_type, type_name))

            # verify the property name is valid for the type
            type_properties = self.get('origins.categories.{}.types.{}.properties'.format(category, type_name),
                                       default={})
            property_name = next(rest)
            # retrieve property details or trigger a KeyError
            property_details = type_properties[property_name]
            yield property_name

            if property_details.get('isMap', default=False):
                # provide map key for mapped properties (e.g. email.headers.transfer-encoding)
                # glue all remaining steps for the map property together (but require at least one)
                yield self._required_map_key(rest)
        except StopIteration:
            # expected another element from next(rest)
            raise IncompleteTracePropertyError()

    @staticmethod
    def _required_map_key(steps):
        # join the remaining / available steps on a dot
        # this results in 'transfer-encoding' if that's the only remaining elements
        # this results in 'nsrl.os.product' if there's three remaining elements 'nsrl', 'os' and 'product'
        map_key = '.'.join(steps)
        if not map_key:
            # empty string, signal an 'incomplete' trace property
            raise IncompleteTracePropertyError()

        return map_key

    def expand(self, name):
        """
        Expands a trace property to 'steps' through a nested data structure.

        Inserts a properties category if unspecified, does *not* include an
        origin.

        :param name: the property name to expand, excluding an origin
        :return: a `tuple` of 'steps'
        :raise ValueError: when a provided *name* is not defined by the trace
            model or is missing required parts
        """
        try:
            if '.' not in name:
                # either an intrinsic property or categorized property without its category
                if name in self.intrinsics:
                    if self.get('properties.{}.isMap'.format(name), default=False):
                        # no dot, missing map key for mapped property (e.g. previews)
                        raise IncompleteTracePropertyError()

                    # return intrinsic property as a one-tuple (e.g. name)
                    return name,

                # categorized property without the specified category (e.g. tags)
                return self._categorized_properties[name], name

            # split the provided name into steps through the model
            steps = iter(name.split('.'))
            step = next(steps)
            if step in self.intrinsics:
                # mapped intrinsic property (e.g. previews.text/plain)
                return step, self._required_map_key(steps)

            if step in self.categories:
                category = step
                step = next(steps)
                if step in self._categorized_properties:
                    if self._categorized_properties[step] != category:
                        raise ValueError('unknown trace property: "{}"'.format(name))

                    # mapped categorized property (e.g. category.misc.something)
                    if self.get('origins.categories.{}.properties.{}.isMap'.format(category, step), default=False):
                        # glue all remaining steps for the map property together (but require at least one)
                        return category, step, self._required_map_key(steps)
                    # regular categorized property (e.g. annotated.tags)
                    return category, step

                # categorized but not a property, must be a categorized type property
                return tuple(self._expand_from_type(category=category, type_name=step, rest=steps))

            if step in self.types:
                # type without category, find corresponding category and expand from there
                category = self._categorized_types[step]
                return tuple(self._expand_from_type(category=category, type_name=step, rest=steps))
        except (StopIteration, IncompleteTracePropertyError):
            # expected another step, raise new error to include full property name in error message
            raise IncompleteTracePropertyError('incomplete trace property: "{}"'.format(name))
        except KeyError:
            raise ValueError('unknown trace property: "{}"'.format(name))
        else:
            raise ValueError('unknown trace property: "{}"'.format(name))

    def get_serializer(self, steps):
        try:
            if self.is_intrinsic(steps):
                converter = CONVERTERS.get(self.get('properties.{}.type'.format(steps[0])))
                return converter.serialize if converter else None

            model_type = self.get('origins.categories.{}.properties.{}.type'.format(*steps[:2]))
            if model_type:
                converter = CONVERTERS.get(model_type)
                return converter.serialize if converter else None

            if steps[1] in self._mapped_types and steps[2] in self._mapped_types[steps[1]]:
                # steps models a mapped type property, steps[2] is the data type name, omit it to retrieve model type
                model_steps = steps[0], steps[1], steps[3]
            else:
                # steps models a regular type property, model type to be retrieved with the first 3 steps
                model_steps = steps[:3]

            model_type = self.get('origins.categories.{}.types.{}.properties.{}.type'.format(*model_steps))
            if model_type:
                converter = CONVERTERS.get(model_type)
                return converter.serialize if converter else None
        except IndexError:
            raise ValueError('unknown trace property: "{}"'.format('.'.join(steps)))
        else:
            raise ValueError('unknown trace property: "{}"'.format('.'.join(steps)))


class TraceBuilder(DictView):
    """
    Utility class to aid in creating user-defined traces or updating existing
    ones. A `.TraceBuilder` is a trace model aware view on a nested mapping,
    using the trace model to both validate requested updates and finding the
    correct spot for values in the nested mapping.

    This class is not intended for direct user instantiation, see

    - `.Trace.child_builder`
    - `.ProjectContext.child_builder`
    - `.TraceBuilder.child_builder`
    """

    def __init__(self, model, source=None, target=None, context=None,
                 debug=False):
        super().__init__(source or {})

        self._model = model
        self._updates = set()
        self._data = {}
        self._context = context
        # mark debug as a 'public' value, enable user to change it later
        self.debug = debug

        self._uid = None

        if isinstance(target, TraceBuilder):
            # target 'parent' is also a TraceBuilder, defer resolving target arguments to a later time
            self._project_id = self._parent_uid = None
            self._parent_builder = target
        elif target:
            # explicit target, no parent builder
            self._project_id, self._parent_uid = target
            self._parent_builder = None
        else:
            # no known target, no issue yet, maybe user will provide target later
            self._project_id = self._parent_uid = self._parent_builder = None

    def update(self, key_or_updates, value=None):
        """
        Add or overwrite new metadata properties to this builder.

        *key_or_updates* can mix dotted properties and nested structures,
        all keys and values are merged before applying updates. A `.TraceModel`
        is used to find the proper fully qualified property names if needed,
        allowing both e.g. ``update('file.name', 'File Name')`` and
        ``update({'extracted': {'file': {'name': 'file name'}}})``.

        :param key_or_updates: either a `str` (the metadata property to be
            updated) or a mapping supplying both keys and values to be updated
            (or `None` if only data is supplied)
        :param value: the value to update metadata property *key* to (used
            only when *key_or_updates* is a `str`)
        :return: this `.TraceBuilder`
        """
        # merge two ways of calling this method into a single data structure
        updates = key_or_updates
        if isinstance(key_or_updates, str):
            updates = {key_or_updates: value}

        # collect all updates in flattened form
        for key, value in flatten_mapping(updates).items():
            # let the trace model expand the key to be updated (will crash for unknown properties)
            steps = self._model.expand(key)
            path, last_step = steps[:-1], steps[-1]

            # enter the user-specified realm for non-intrinsic properties
            current = self._source
            if not self._model.is_intrinsic(steps):
                current = current.setdefault('user', {})

            # walk through the source to arrive at the last stop
            for step in path:
                current = current.setdefault(step, {})

            # find a serializer and set the actual value where's it's supposed to go
            serializer = self._model.get_serializer(steps)
            current[last_step] = serializer(value) if serializer else value

            # track that we've applied an update for the steps just taken
            self._updates.add('.'.join(steps))

        return self

    def add_data(self, stream, data):
        """
        Add data to this trace as a named stream.

        :param stream: name of the data stream to be added
        :param data: data to be attached
        :return: this `.TraceBuilder`
        """
        if stream not in self._model.data_types:
            log.warn('data type stream name "{}" not defined by model, '
                     'trace being constructed might be invalid', stream)

        self._data[stream] = data

        return self

    @property
    def updates(self):
        """
        A collection of updates tracked by this `.TraceBuilder`.
        """
        # create a deterministic view on the updates this builder has applied to its source
        return tuple(sorted(self._updates))

    @property
    def context(self):
        """
        The `ProjectContext <hansken.remote.ProjectContext>` instance that
        created this `.TraceBuilder`.
        """
        if self._context:
            return self._context
        else:
            raise ValueError('project context for trace builder not set')

    @property
    def target(self):
        """
        The combination of *(project id, parent trace uid)* this
        `.TraceBuilder` applies to.
        """
        if self._project_id and self._parent_uid:
            return self._project_id, self._parent_uid
        elif self._parent_builder is not None:  # NB: an empty parent builder is falsy
            if not self._parent_builder._uid:
                raise ValueError('parent builder has no uid (yet), missing builder target parameters')
            # use parent's project id and parent's uid as the target for this builder
            return self._parent_builder._project_id, self._parent_builder._uid
        else:
            raise ValueError('builder target missing project id and/or parent trace uid')

    def child_builder(self, name=None):
        """
        Creates a new `.TraceBuilder` to build a child trace to the trace to be
        represented by this builder.

        .. note::

            Parent `.TraceBuilder`s should be built using the `.build()` call
            *before* their child builders as the unique trace identifier (uid)
            for the parent is needed to build a child trace.

        :param name: name of the new child trace
        :return: a `.TraceBuilder` set up to save a new trace as the child
            trace of this builder
        """
        # create an instance of our own type, supply all the arguments the child builder needs
        builder = type(self)(model=self._model, target=self, context=self._context, debug=self.debug)

        if name:
            # optionally add a name for the new child trace
            builder.update('name', name)

        return builder

    def build(self):
        """
        Save the trace being built by this builder to remote.

        .. note::

            If this `.TraceBuilder` was put in debug mode, the trace is *not*
            sent to remote but is instead logged at warning level.

        :return: the new trace' uid (or `None` in debug mode)
        """
        if self.debug:
            def value_path(key):
                if self._model.is_intrinsic(self._model.expand(key)):
                    return key
                else:
                    return 'user.{}'.format(key)

            log.warning(
                '{builder.__class__.__module__}.{builder.__class__.__name__} in debug mode, not creating with with '
                'parent {parent}; properties: {updates}; data: {data}',
                builder=self, parent=self.target[1], updates=', '.join(self.updates), data=', '.join(
                    '{}: {} bytes'.format(name, len(stream))
                    for name, stream in sorted(self._data.items())
                ) or '(no data)'
            )
            # collect update values only, apply the inverse of update's handling of intrinsic / user values
            # (updates are collected without the origin prefix)
            update_info = {key: self.get(key) for key in map(value_path, self.updates)}
            # mimic a REST trace, log the trace in JSON format (value serialization is already done by update)
            update_info = json.dumps(update_info, ensure_ascii=False, indent=2)
            log.debug('trace not created: \n{trace}', trace=update_info)

            return None
        else:
            if self._uid:
                # avoid creating duplicates from the same builder
                raise ValueError('builder was already built (resulting uid: {})'.format(self._uid))

            log.debug(
                'submitting {builder.__class__.__module__}.{builder.__class__.__name__} as a new trace with '
                'parent {parent}; properties: {updates}; data: {data}',
                builder=self, parent=self.target[1], updates=', '.join(self.updates), data=', '.join(
                    '{}: {} bytes'.format(name, len(stream))
                    for name, stream in sorted(self._data.items())
                ) or '(no data)'
            )
            self._uid = self.context.connection.create_trace(*self.target, self, data=self._data)
            return self._uid


def value_converter_for(property_details):
    """
    Creates a trace value converter for a provided property value definition.
    Key "type" in *property_details* primarily defines the conversion. The
    following trace value types are converted:

    - *date*: a `datetime.datetime` object with timezone
    - *binary*: a `bytes` object

    If *property_details* states that the the value will be a sequence,
    mapping or mapping to sequences, the created converter will take this into
    account.

    :param property_details: a property definition dict
    :return: a callable that converts a wire format to a python type, or
        ``None`` (no conversion needed or supported)
    """
    def sequence_converter(converter):
        # transform the sequence of raw values to a sequence of transformed values
        return lambda values: [converter(value) for value in values]

    def mapping_converter(converter):
        # transform the mapped values to an equivalent dict of converted values with the same mapping
        return lambda values: {key: converter(value) for key, value in values.items()}

    # converter for value type defined in the trace model
    converter = CONVERTERS.get(property_details.get('type'))
    converter = converter.deserialize if converter else None

    if converter:
        # the value has a converter, check to see if we'll be getting sequences or mappings
        # NB: this means that a mapping of lists is possible ({'key': ['value', 'value', …]})!
        if property_details.get('isList'):
            converter = sequence_converter(converter)
        if property_details.get('isMap'):
            converter = mapping_converter(converter)

    # whether still None or constructed to be something fancy, converter is now what it needs to be
    return converter


def trace_types(model):
    """
    Reduces a trace model dict to the bare essentials used to define the
    properties of a trace, e.g.:

    .. code-block:: python

        {('extracted', 'file'): {'name': None,  # name is a str, no conversion needed
                                 'createdOn': iso8601.parse_date}}

    :param model: the full trace model received from remote
    :return: a mapping that maps a trace type's category and name to its
        properties defined in the model along with a converter for the
        property's type (or ``None``), again as a mapping
    """
    essentials = {}

    for category, types in model['origins']['categories'].items():
        # (some categories can be empty)
        if types:
            # get the name of the trace type and whatever the trace model defines for that type
            for type_name, trace_type in types['types'].items():
                # reduce the details for all the trace type's properties to just its type
                properties = {prop: value_converter_for(details)
                              for prop, details
                              in trace_type['properties'].items()}
                essentials[(category, type_name)] = properties

    return essentials


def expand_types(model, *type_names):
    """
    Creates a `list` of property names for the requested trace types, obtained
    from the provided model. Resulting property names are formatted as
    ``<trace_type>.<property_name>``, e.g. ``'file.createdOn'``.

    :param model: the model to read types and properties from
    :param type_names: the names of the types to be expanded
    :return: a `list` of typed property names
    """
    names = []
    model_types = model['origins']['categories']['extracted']['types']
    for type_name in type_names:
        # generate property names including their type names (sorted to force deterministic behaviour)
        names.extend(sorted('{}.{}'.format(type_name, prop)
                            for prop in model_types[type_name]['properties'].keys()))

    return names


class TraceTypeView(DictView):
    """
    Utility class to turn a trace's type into a prefixed view on the trace's
    source dict.
    """

    def __init__(self, source, name, category, origins=('system', 'user'), converters=None):
        """
        Create a new trace type view.

        :param source: trace source
        :param name: name of the trace type
        :param category: category where the named type resides
        :param origins: origins where the trace type could be sourced from,
            ordered by priority
        :param converters: mapping of property names to optional type
            converter (a `callable`)
        """
        super().__init__(source)

        self._name = name
        self._category = category
        self._origins = origins

        self._converters = converters or {}

    def get(self, key, default=None):
        for origin in self._origins:
            # see if there's a value for <origin>.<category>.<name>.<key>
            value = super().get(self._separator.join((origin, self._category, self._name, key)),
                                default=self._no_default)
            if value is not self._no_default:
                # found a valid value
                converter = self._converters.get(key)
                return converter(value) if converter else value

        # no origin has a value for key in source
        return default

    def keys(self):
        keys = set()
        for origin in self._origins:
            # retrieve trace type for each origin
            origin_type = super().get(self._separator.join((origin, self._category, self._name)))
            if isinstance(origin_type, Mapping):
                # create a union of keys in each origin, if available
                keys.update(origin_type.keys())

        return keys

    def __iter__(self):
        # self._source is not rooted at the trace type, override to use keys at the view point
        return iter(self.keys())

    def __len__(self):
        # self._source is not rooted at the trace type, override to use keys at the view point
        return len(self.keys())

    def __str__(self):
        # NB: comprehensions create their own scope, causing zero-argument super() to fail inside them, create a
        #     super-proxy inside the __str__ def to be able to use it inside the comprehension
        parent = super()
        # super's __str__ would return a str() of the entire source
        # create a str of all the chunks of data that would be available through get(), keyed by the chunk/origin's name
        return str({origin: parent.get('.'.join((origin, self._category, self._name)))
                    for origin in self._origins})

    def __repr__(self):
        return '<{0.__class__.__module__}.{0.__class__.__name__} ({0._name})>'.format(self)


def trace_class_from_model(model):
    """
    Creates a Trace class definition from the provided model. Both intrinsic
    properties and the properties defined for each type are automatically
    defined for the class and will be None should they not be present on the
    actual trace instance.

    The constructor for the resulting class accepts a single argument, being
    a dict as received from remote, with properties defined by model. See
    `.DictView` for access patterns for instances of the resulting class.

    :param model: the full trace model received from remote
    :return: a class definition for a Trace defined by model
    """
    # read intrinsic properties from model
    intrinsics = {prop: value_converter_for(details)
                  for prop, details
                  in model['properties'].items()}
    # create an unnamed view class from the intrinsic properties (used as a super for TraceView, setting intrinsics)
    intrinsic_view = view_with_attrs(attrs=intrinsics)

    # determine the origins defined by the model
    # NB: current client and server implementations don't care about the order defined here, this may change in the
    #     future™, sorted here to ensure deterministic behaviour
    origins = sorted(model['origins']['keys'].keys())
    categories = model['origins']['categories'].keys()

    # create {(category, name) → {prop_name → converter}} mapping from the model
    model_types = trace_types(model)
    # create a reverse lookup to find the category of a type
    types = {name: category for category, name in model_types.keys()}

    # determine many and mapped trace types
    many_types = set()
    mapped_types = set()
    for category, type_name in model_types.keys():
        trace_type = model['origins']['categories'][category]['types'][type_name]
        # many-type defined by isList: true or few/many cardinality
        if trace_type.get('isList') or trace_type.get('cardinality') in ('few', 'many'):
            many_types.add((category, type_name))
        # map-typed defined by "keys" being non-empty
        if trace_type.get('keys'):
            mapped_types.add((category, type_name))

    # create a trace type class for each trace type defined by the model using type:
    # - new type is named alike extracted.text_message (builtin type's module "abc" is prefixed in __repr__)
    # - new type inherits from
    #   - TraceTypeView, able to get() values from a trace's deeply nested source dict
    #   - an AttrView, making attribute access easier, calling get() (defined by TraceTypeView) to get the respective
    #     values
    # - define no additional class variables
    type_classes = {(category, type_name): type('.'.join(map(to_attr_name, (category, type_name))),
                                                (TraceTypeView, view_with_attrs(type_name, properties.keys())),
                                                {})
                    for (category, type_name), properties in model_types.items()}

    # NB: the order of super classes is significant here, Trace needs the context argument, intrinsic_view (an
    #     AttrView) won't like it, method resolution order will make Trace.__init__ call intrinsic_view.__init__
    #     instead of DictView.__init__
    class TraceView(Trace, intrinsic_view):
        def __init__(self, source, context=None):
            super().__init__(source, context)

            # collect categorized types defined for this trace, regardless of origin
            types = set()
            for origin in origins:
                origin = self.get(origin) or {}
                for category_name, category in origin.items():
                    types.update({(category_name, type_name)
                                  for type_name in category.keys()
                                  # drop any non-defined (category, type) combo's (like (annotated, tags))
                                  if (category_name, type_name) in model_types.keys()})

            # set trace type attributes to self
            for category_name, type_name in types:
                type_class = type_classes[(category_name, type_name)]

                if (category_name, type_name) in mapped_types:
                    # gather the keys (typically data types) defined for this trace type in any origin
                    keys = set(chain.from_iterable((self.get('.'.join((origin, category_name, type_name))) or {}).keys()
                                                   for origin in origins))
                    type_attr = view_with_attrs(to_attr_name(type_name), keys)
                    setattr(self,
                            to_attr_name(type_name),
                            type_attr({
                                # include key name to type name to make TraceTypeView construct the right selection key
                                key: type_class(source,
                                                '.'.join((type_name, key)), category_name, origins,
                                                converters=model_types.get((category_name, type_name)))
                                for key in keys
                            }))
                elif (category_name, type_name) in many_types:
                    # make Trace class deal with many types
                    pass
                else:
                    setattr(self,
                            to_attr_name(type_name),
                            type_class(source,
                                       type_name, category_name, origins,
                                       converters=model_types.get((category_name, type_name))))

            # assign a set of type names to self
            self.types = {type_name for _, type_name in types}

        def get(self, key, default=None):
            # override DictView.get with a model-aware variant, allowing
            # 1. get('origin.category.type.property')
            # 2. get('category.type.property')
            # 3. get('type.property')
            # while not breaking
            # get('origin.category.type'), get('category.type'), get('category'), get('type'), get('origin.category'),
            # get('origin'), get('origin.type')
            steps = key.split(self._separator)

            candidate_origins = origins
            if steps[0] in origins and len(steps) >= 4:
                # explicit option 1, strip the origin from steps to hit conditions below while restricting the origins
                # that need to be checked
                candidate_origins = [steps.pop(0)]

            if steps[0] in types:
                # first key is a known type, insert its category (types is {name → category}) and move on
                steps.insert(0, types.get(steps[0]))

            if steps[0] in categories:
                # (new) first step is a category, return first available <origin>.<category>.<type>.<rest>
                # (depending on code above, there may be only one origin that needs to be checked)
                for origin in candidate_origins:
                    value = super().get(self._separator.join([origin] + steps), default=self._no_default)
                    if value is not self._no_default:
                        # value is available, figure out if it needs a type conversion
                        modeled = model_types.get((steps[0], steps[1]))
                        if modeled and len(steps) >= 3:
                            # determine the step that contains the actual property name
                            # (1 index further along for mapped types)
                            property_step = steps[2 if (steps[0], steps[1]) not in mapped_types else 3]
                            converter = modeled.get(property_step)
                            if converter:
                                # converter defined for value, apply
                                return converter(value)

                        return value

            # either option 1 or non-understandable or non-model key, use default implementation
            return super().get(key, default)

    type_doc = """Trace type attributes added from model: {}.

Trace type attributes are defined when a trace has that particular
trace type. Check for this with `'type_name' in trace.types`.""".format(
        ', '.join(to_attr_name(name) for _, name in model_types.keys())
    )
    TraceView.__doc__ = '{}\n\n{}'.format(Trace.__doc__, type_doc)

    return TraceView
