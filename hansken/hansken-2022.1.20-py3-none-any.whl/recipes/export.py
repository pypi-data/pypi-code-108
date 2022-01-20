# encoding=utf-8

from concurrent.futures import as_completed, FIRST_COMPLETED, ThreadPoolExecutor, wait
import csv
from functools import partial
from io import open  # this is essentially meaningless, but makes it possible to mock calls to open()
from os import makedirs, path
import re

from logbook import Logger

from hansken import fetch
from hansken.trace import expand_types


log = Logger(__name__)


def get_fields(trace, fields, prefix='system.extracted.', use_fallback=True, default=None):
    """
    Retrieves values for fields from source by calling
    source.get(prefix + field) for each field.

    :param trace: collection of mapped values
    :param fields: fields to retrieve a value for
    :param prefix: prefix used with get
    :param use_fallback: whether to try getting a field without prefix when
        a value for the full field name is not available
    :param default: value to use when no value was mapped
    :return: a dictionary with all of the requested fields and their value in
        the source of *trace*, or `None` if *trace* has no value for the field
    :rtype: `dict`
    """
    values = {}
    for field in fields:
        if isinstance(field, data_stream):
            log.info('retrieving {} stream for trace {}', field, trace.uid)
            values[field.field_name] = field.to_text(trace, default=default)
        else:
            value = trace.get('{prefix}{field}'.format(prefix=prefix or '', field=field), default=default)
            if value is None and use_fallback:
                # fallback to property without prefix only if allowed and value is None (0 or False are valid)
                value = trace.get(field, default=default)
            # collect
            values[field] = value

    return values


class type_fields:  # noqa: N801
    """
    An object to request that all fields of the requested types should be used
    as field names when exporting to CSV format. Multiple type names can be
    provided:

    .. code-block:: python

        to_csv(..., fields=type_fields('file', 'link'))
        # supplying two types at once is equivalent to supplying two separate type_fields
        to_csv(..., fields=[type_fields('file'), type_fields('link'))

    Both forms would result in headers like ``file.createdOn`` and
    ``link.target`` in the resulting export file.
    """
    # TODO: include_intrinsics, handle_list, handle_dict/map
    def __init__(self, *type_names):
        self.type_names = type_names


class data_stream:  # noqa: N801
    """
    An object to request text data for traces to be exported. Like
    `.type_fields`, this can be mixed with regular metadata fields:

    .. code-block:: python

        to_csv(..., fields=['data.raw.size', data_stream('raw', max_size=1024)])
        to_csv(..., fields=data_stream('text', max_size=None))

    A fallback text encoding can be provided for data stream exports that have
    no explicit or known text encoding:

    .. code-block:: python

        to_csv(..., fields=data_stream('plain', fallback_encoding='ascii')

    Encoding errors will result in replacement characters — ?'s — in the output
    CSV. The fallback encoding is unset by default, resulting in *no data* in
    the output CSV.

    For custom functionality (like including binary data encoded as hex or
    base64), this class can be extended. `.to_text` is called by the exporter
    (`.get_fields` when `.to_csv` is used) to get a `str` from a `.Trace` being
    exported.

    .. note::

        The maximum number of bytes that are read from the stream defaults to
        4KiB. While it's possible to include an entire data stream in the
        export, please note that data streams can grow quite large; use this
        with caution.

    .. note::

        As exporting data requires an additional HTTP request for each data
        stream of each `.Trace` being exported, including data in an export
        slows down the export considerably.
    """
    # data stream names that are known to contain utf-8 encoded text
    utf8_data_types = ('html', 'htmlText', 'ocr', 'text')
    # data streams other than those above might contain an explicit charset in their mime type
    encoding_pattern = re.compile(r"""charset=['"]?(?P<encoding>[\w\-]+)['"]?""")

    def __init__(self, data_type, max_size=4 << 10, fallback_encoding=None):
        self.data_type = data_type
        self.max_size = max_size
        self.fallback_encoding = fallback_encoding

    @property
    def field_name(self):
        return 'data.{}'.format(self.data_type)

    def get_encoding(self, trace):
        mime_type = trace.get('data.{}.mimeType'.format(self.data_type))
        encoding = self.encoding_pattern.search(mime_type) if mime_type else None
        if encoding:
            return encoding.group('encoding').lower()
        elif self.data_type in self.utf8_data_types:
            return 'utf-8'
        elif self.fallback_encoding:
            log.debug('falling back to encoding {} for stream {} of trace {}',
                      self.fallback_encoding, self.data_type, trace.uid)
            return self.fallback_encoding
        else:
            log.debug('unable to determine encoding of stream {} for trace {} (mime type: {})',
                      self.data_type, trace.uid, mime_type)
            return None

    def to_text(self, trace, default=None):
        """
        Get a `str` from a `.Trace`. Uses this `.data_stream`'s ``data_type``
        and ``max_size`` to retrieve the requested data and turns it into a
        `str` if possible.

        :param trace: the `.Trace` being exported
        :param default: the value to be used when retrieving the data or
            turning it into a `str` fails
        :return: a `str` representation of (a part of) the requested data
            stream
        """
        if self.data_type not in trace.data_types:
            return default

        encoding = self.get_encoding(trace)
        if not encoding:
            log.warn('omitting data for stream {} for trace {}, '
                     'unable to determine encoding and no fallback encoding provided', self.data_type, trace.uid)
            return default

        with trace.open(self.data_type, size=self.max_size) as data:
            data = data.read()
            return data.decode(encoding, errors='replace')


def to_csv(traces, output, fields,
           to_dict=get_fields,
           delimiter='\t',
           lineterminator='\n',
           encoding='utf-8',
           **fmtparams):
    """
    Writes values for fields from each trace in *traces* to *output*. Field
    names can be supplied as property names (e.g. ``'file.createdOn'``) or as
    `.type_fields` instances that automatically expand to properties defined
    for the specified types. Data can be included by using `.data_stream`
    instances.

    .. note::

        Using `.type_fields` instances **requires** that the *traces* argument
        carries the applicable trace model as attribute ``model``. Using
        `.data_stream` instances **requires** that the `.Trace` objects in the
        *traces* argument carry a `.ProjectContext` object. This is the case
        for `.SearchResult` instances obtained from calls like
        `.ProjectContext.search`:

        .. code-block:: python

            # obtain search results as normally
            results = context.search('query')
            # export the results to a local CSV file
            to_csv(results, 'path/to/export.csv',
                   # explicit fields and automatically expanded fields can be mixed
                   fields=['uid', 'name',
                           # include all model-defined metadata fields for email traces
                           type_fields('email'),
                           # include the first kilobyte of data from the plain data stream (converted to text)
                           data_stream('plain', max_size=1024)

        The exported file with have the explicitly provided fields like ``uid``
        and ``name``, but also fields from property names generated from the
        trace model retrieved from the `.ProjectContext`, like
        ``email.subject`` and ``email.to``. The `.data_stream` instance will
        cause a ``data.plain`` field.

    :param traces: collection of traces
    :param output: name of the file to write to
    :param fields: fields to retrieve values for, a sequence of property names
        (`str`) or `.type_fields` instances, used to generate field and
        property names from a trace type
    :param to_dict: callable to create a dict ``{field: value}``;
        passed kwargs: *trace*, *fields*
    :param delimiter: field delimiter in the output
    :param lineterminator: line terminator in the output
    :param encoding: text encoding for the output
    :param fmtparams: additional format parameters, see module csv in the
                      standard lib
    """
    def expand(fields):
        """
        Recursively resolves any instances of `type_fields` to the corresponding
        properties / field names and adds a field name to any `data_stream`
        instances. Yields *(name, field)* tuples, where the field name
        will only differ from the field for `data_stream` instances.
        """
        if isinstance(fields, str):
            # fields is just a field
            yield fields, fields
        elif isinstance(fields, data_stream):
            # fields is a data stream, handled in get_fields
            yield fields.field_name, fields
        elif isinstance(fields, type_fields):
            # user request to include all properties for a type
            for field in expand_types(traces.model, *fields.type_names):
                yield field, field
        else:
            # sequence of fields, resolve any type_fields instances
            for item in fields:
                yield from expand(item)

    # will use builtin csv module, open the file in text mode, *don't* translate line endings to os default
    # (by supplying lineterminator to the writer, a script would produce identical output on any os)
    output = open(output, 'w', newline='', encoding=encoding)

    # resolve any 'automatic headers' passed as type_fields instances, split fields names and field 'pointers'
    names, fields = zip(*expand(fields))
    with output:
        writer = csv.DictWriter(output,
                                fieldnames=names,
                                delimiter=delimiter,
                                lineterminator=lineterminator,
                                **fmtparams)
        writer.writeheader()
        for trace in traces:
            writer.writerow(to_dict(trace=trace, fields=fields))


def to_file(trace, output, stream='raw', offset=0, size=None, key=fetch, bufsize=1 << 20):
    """
    Writes a data stream of a trace to a file.

    :param trace: trace to write
    :param output: name of the file to write to
    :param stream: named stream to read from the trace
    :param offset: byte offset to start the stream on
    :param size: the number of bytes to make available
    :param key: key for the image of *trace* (default is to fetch the key
        automatically, if it's available)
    :param bufsize: buffer size to be used during the read/write loop
    """
    with open(output, 'wb') as out_file, trace.open(stream=stream, offset=offset, size=size, key=key) as stream:
        # pre-allocate a reusable buffer
        buffer = memoryview(bytearray(bufsize))
        # keep reading into buffer until we reach the end of the stream
        num_read = stream.readinto(buffer)
        while num_read:
            out_file.write(buffer[:num_read])  # only write up to num_read, we don't want trailing junk
            num_read = stream.readinto(buffer)


def safe_name(trace, num=None, split=1000, stream='raw', template='{trace.image_id}_{trace.id}_{stream}_{trace.name}'):
    """
    Generate a file name for a trace. Resulting file name can contain unicode
    characters, but no slashes, backslashes or line endings.

    :param trace: trace to name
    :param num: the number of this trace within the set being exported
    :param split: the max number of files in a directory
    :param stream: the named stream to be exported
    :param template: format string used as the file name, slashes and newlines
        are replaced by underscores in the result;
        passed kwargs: *trace*, *num*, *split*, *stream*
    :return: generated file name
    """
    file_name = template.format(trace=trace,
                                num=num,
                                split=split,
                                stream=stream)
    # NB: unicode characters in trace names are assumed to be safe
    return re.sub(r'[/\\\n\r]', '_', file_name.strip())


def bulk(traces, dest, split=1000, stream='raw', fname=safe_name, write=to_file, on_error=None, side_effect=None,
         jobs=16):
    """
    Performs a bulk export of traces to dest.

    .. note::

        `.bulk` is internally parallellized by default, **requiring** that the
        argument to *write* is thread-safe. *safe_name*, *on_error* and
        *side_effect* are all called from the calling thread after the export
        of a particular trace in *traces* was processed.

        As *on_error* is **not** called from the ``except`` clause that catches
        the `Exception` instance, logging the exception with its traceback
        requires special care to pass the ``exc_info`` keyword to either
        `logging` or `logbook`. Leaving *on_error* as `None` will raise a
        `ValueError` on the thread calling `bulk` with the error that is
        processed first as its cause.

        This also means that the order of traces with which *write*, *on_error*
        and *side_effect* are called need not be the same order as that of
        *traces*. To turn this parallellism off, pass ``jobs=False``.

    :param traces: collection of traces to export
    :param dest: path to export traces to
    :param split: max number of files per directory (when set to `None`, all
        files will be saved to the same directory)
    :param stream: stream name to read from the traces, optionally supplied as
        a `callable` returning the stream name;
        passed kwargs: *trace*
    :param fname: `callable` to generate a file name for a trace;
        passed kwargs: *trace*, *num*, *split*, *stream* (defaults to
        `.safe_name`, resulting in a file name that uses both
        ``trace.image_id`` and ``trace.id``, ensuring the name is unique
        within a project)
    :param write: *thread-safe* `callable` to write a trace to a file name;
        passed kwargs: *trace*, *output*, *stream* (defaults to `.to_file`)
    :param on_error: `callable` to report an error thrown during ``write()``;
        passed kwargs: *num*, *trace*, *stream*, *output*, *exception*
    :param side_effect: `callable` to perform a side effect for each exported
        trace;
        passed kwargs: *trace*, *stream*, *num*, *split*, *dest*, *folder*,
        *file*, *output*
    :param jobs: maximum number of data exports to run in parallel (an `int`),
        or `False` to turn parallel processing of *traces* off
    :raises ValueError: on the first error result when *on_error* is not
        supplied (the error is set as the cause)
    """
    if jobs is True or not isinstance(jobs, int):
        raise TypeError('an int or False is required for arguments jobs')

    num_total = len(traces)
    # determine the ideal length of the folder names for split sets
    order = len(str(num_total // split)) if split else 1

    try:
        executor = ThreadPoolExecutor(max_workers=jobs or 1, thread_name_prefix='bulk_export_worker')
    except TypeError:
        # thread_name_prefix is not supported for Python 3.5 (backport for 2.7 *does* have this argument)
        executor = ThreadPoolExecutor(max_workers=jobs or 1)

    with executor:
        # track pending tasks as a set of futures
        futures = set()
        # allow a fixed number of tasks to be pending
        pending_threshold = jobs * 2 if jobs else 1
        # prepare a call to run_task needing only a task
        target = partial(run_task, write)

        for num, trace in enumerate(traces):
            # resolve stream if caller wants to decide which one to select
            selected_stream = stream(trace=trace) if callable(stream) else stream
            # determine folder number only if a split is requested
            folder = num // split if split else None
            file = fname(trace=trace, num=num, split=split, stream=selected_stream)

            if folder is not None:
                folder = path.join(dest, '{folder:0{len}}'.format(folder=folder, len=order))
            else:
                # no need to insert a split number folder
                folder = dest

            makedirs(folder, exist_ok=True)

            output = path.join(folder, file)

            # define task as a collection of locals needed by write to complete the task
            task = {
                'trace': trace, 'stream': selected_stream,
                'num': num, 'split': split,
                'dest': dest, 'folder': folder, 'file': file, 'output': output,
            }
            # submit the execution of task to the executor, tracking the future for … future use
            futures.add(executor.submit(target, task))

            # 'periodically' check how many tasks are currently tracked
            # (this provides 'back pressure' on consuming traces and avoids flooding the executor queue)
            if len(futures) >= pending_threshold:
                # retrieve the futures that are already done or wait for the first one to be done
                done, _ = wait(futures, return_when=FIRST_COMPLETED)
                # untrack the done futures (effectively creating len(done) space for new tasks to be submitted)
                futures.difference_update(done)

                # process the results of all the done tasks
                for future in done:
                    task, error = future.result()
                    process_result(task, error, on_error, side_effect)

        # traces has been consumed, all tasks submitted, wait for and process all tasks still pending
        for future in as_completed(futures):
            task, error = future.result()
            process_result(task, error, on_error, side_effect)


def run_task(write, task):
    """
    Runs *task* using *write*.

    *(Intended for internal use with `.bulk`)*

    :param write: *thread-safe* callable to write a trace to a file name;
        passed kwargs: *trace*, *output*, *stream* (defaults to `.to_file`)
    :param task: the task to perform using *write*
    :return: a 2-tuple *(original task, optional error)*
    """
    try:
        # save trace' stream to the generated output path
        write(trace=task['trace'], output=task['output'], stream=task['stream'])
        return task, None
    except Exception as e:
        return task, e


def process_result(task, error, on_error, side_effect):
    """
    Processes the result of *task*, calling *side_effect* on success,
    *on_error* on failure.

    *(Intended for internal use with `.bulk`)*

    :param task: the task that was performed
    :param error: an optional error encountered while performing *task*
    :param on_error: callable to report an error thrown during ``write()``;
        passed kwargs: *num*, *trace*, *stream*, *output*, *exception*
    :param side_effect: callable to perform a side effect for each exported
        trace;
        passed kwargs: *trace*, *stream*, *num*, *split*, *dest*, *folder*,
        *file*, *output*
    :raise ValueError: when *error* is provided and *on_error* is not (note
        that an error raised by *side_effect* counts as *error* being provided)
    """
    if not error and callable(side_effect):
        try:
            # call the side effect with a lot of info:
            side_effect(
                # info on the stream being exported
                trace=task['trace'], stream=task['stream'],
                # split info
                num=task['num'], split=task['split'],
                # destination path (and parts)
                dest=task['dest'], folder=task['folder'], file=task['file'], output=task['output']
            )
        except Exception as e:
            error = e

    if error:
        if callable(on_error):
            on_error(num=task['num'], trace=task['trace'], stream=task['stream'], output=task['output'],
                     exception=error)
        else:
            raise ValueError('export or side effect of trace {} failed'.format(task['trace'].get('uid'))) from error
