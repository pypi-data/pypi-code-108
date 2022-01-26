#!/usr/bin/python
"""
    out.py                           Nat Goodspeed
    Copyright (C) 2015               Nat Goodspeed

Python generators imply a natural composition idiom:

def filter(iterable):
    for item in iterable:
        # do something and then
        yield item

Such generators can readily be chained to construct arbitrary pipelines.

The introduction of reverse data flow ('yield' returning a result) permits
chains of output generators ('push' generators) as well. Which processing
belongs in an input chain and which in an output chain? The answer depends on
where you put the driving loop. For example:

    from pyng.genio import filesink, filesource
    filesink(outname, filter(filesource(inname)))

The above chain is driven by the loop in filesink(), the ultimate destination.
Therefore all the rest of the processing can be performed using input
generators.

I have yet to encounter an equally obvious idiom for output chains. (To be
fair, the community may have adopted one without my being aware of it.) One
reasonable choice is to base the API on file-like objects, at least a subset
of the output-related methods:

class ofilter(object):
    def __init__(self, sink):
        self.sink = sink

    def write(self, item):
        # do something and then
        self.sink.write(item)

    def flush(self):
        self.sink.flush()

Though the above trivial filter doesn't require output-generator
machinery, it supports it. (See, for example, buffer_lines below.)

Such output filters can be composed as:

    with open(outname, 'w') as outf:
        sink = ofilter1(ofilter2(outf))
        for line in open(inname):
            sink.write(line)

NRG 2015-11-07
"""

import atexit
from collections import namedtuple
from contextlib import contextmanager
import datetime
from functools import wraps
import json
import logging
from pyng.exc import exceptlink, describe
import syslog

class OutError(Exception):
    pass

def push_generator(func):
    """
    Decorate a push generator such that calling it returns a handle on which
    you can call send(), throw(), close() et al.

    @push_generator
    def file_writer(filename):
        with open(filename, 'w') as outf:
            while True:
                outf.write(yield)

    Usage:

    with closing(file_writer('somefile.txt')) as writer:
        writer.send('some text')
        # ...
    """
    @wraps(func)
    def wrapper(*args, **kwds):
        return pushiter(func(*args, **kwds))
    return wrapper

def pushiter(generator_call):
    """
    Return an iterator into a generator coded to accept values via 'yield': a
    push generator. Typical usage of such an iterator would be something like:

    handle = iter(generator_call(args...))
    next(handle)                # MUST run it up to first yield!
    handle.send(...)            # now can start pushing values

    pushiter() simply encapsulates that required first next() call.
    If your generator actually engages in bidirectional handshakes, and the
    first yield produces a meaningful value, of course use iter() and next()
    directly.
    """
    handle = iter(generator_call)
    next(handle)                # run the generator to the first yield
    return handle

class ofilter(object):
    """
    The output filter API is primarily write() and (optionally) flush(). But
    it can be convenient to emulate other file-like output methods, permitting
    your filter to be passed to functions expecting an open output file.
    Derive from this class, overriding whatever you need.
    """
    def __init__(self, sink=None, **kwds):
        self.sink = self._maybe_adapt(sink, **kwds)

    @property
    def name(self):
        """
        Actual filesystem file objects returned by open() have a 'name'
        attribute. Allow querying that attribute from our sink, using this
        read-only property.
        """
        # There seems little point in caching the sequence of attempts below,
        # since how many times do we expect a caller to query a file's name
        # attribute? It's not going to change!
        try:
            # Assume self.sink has a name.
            return self.sink.name
        except AttributeError:
            try:
                # self.sink might not be a filesystem file. Just return the
                # object's name (e.g. a function).
                return self.sink.__name__
            except AttributeError:
                # no __name__? then just repr()
                return repr(self.sink)

    def _maybe_adapt(self, sink=None, **kwds):
        """
        We expect the passed sink to be itself a file-like object, at least to
        the extent of supporting write() and flush(). But we facilitate one
        other use case: a sink consisting of a unary callable. For instance,
        you might pass write=mylist.append as the sink to one of our
        subclasses. Therefore subclasses should call this method to properly
        interpret their sink param.
        """
        try:
            write = kwds.pop("write")
        except KeyError:
            # No write= override: does the sink parameter have a write()
            # method?
            try:
                sink.write
            except AttributeError:
                raise OutError("%s passed invalid sink %s" %
                               (self.__class__.__name__, sink.__class__.__name__))
            # sink has a write() method, how about flush()?
            try:
                sink.flush
            except AttributeError:
                # Caller will expect flush(). Construct an adapter whose
                # write() will call sink.write(), and whose flush() is a
                # no-op.
                return adapter(sink.write)
            else:
                # sink has both write() and flush(), use it directly
                return sink
        else:
            # Caller explicitly passed write=something. Construct an adapter
            # with the caller's write() and perhaps flush() callables.
            return adapter(write, kwds.pop("flush", None))

    def write(self, item):
        # do something and then
        self.sink.write(item)

    def writelines(self, iterable):
        for item in iterable:
            self.write(item)

    def flush(self):
        self.sink.flush()

    def close(self):
        self.flush()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()
        # don't eat any exception
        return False

class adapter(ofilter):
    """
    Wrap an arbitrary write() callable (and perhaps a separate flush()
    callable) as a file-like object.
    """
    def __init__(self, write, flush=None):
        # We do not forward the call to base-class __init__(), therefore we
        # have no self.sink attribute.
        self.write = write
        if flush:
            self.flush = flush

    def flush(self):
        # Have to override flush() method so we don't call base-class one that
        # references self.sink.
        pass

class _Flush(Exception):
    """Exception used internally by buffer_lines"""
    pass

class buffer_lines(ofilter):
    """
    Certain output libraries (e.g. syslog) produce a distinct line of output
    for each call. While you can readily fake up a file-like object whose
    write() method writes to syslog, the fact that Python I/O frequently
    writes partial lines can be a problem. An ordinary print statement calls
    write() at least twice: once for each item, once for the space implied by
    each comma between items, with a final call for the newline character.
    pprint.pprint() writes each item separately.

    This output filter assembles complete lines from multiple calls.
    """
    def __init__(self, sink=None, **kwds):
        """
        Pass eol='\n' if you want a newline on each line passed through
        sink(). Otherwise the newline character is eaten.
        """
        self.eol = kwds.pop("eol", '')
        self.loopgen = self.loop(self._maybe_adapt(sink, **kwds))

    def write(self, item):
        # cause loop()'s (yield) to return the passed item
        self.loopgen.send(item)

    def flush(self):
        # pending buffer can be flushed simply by sending a newline
        self.write('\n')
        # but then also flush sink
        self.loopgen.throw(_Flush)

    def close(self):
        self.flush()
        self.loopgen.close()

    @push_generator
    def loop(self, sink):
        # start with an empty string so we always have a buffer[-1]
        buffer = [""]
        # loop forever
        while True:
            # until the most recent item contains at least one newline
            while '\n' not in buffer[-1]:
                try:
                    # accumulate items
                    buffer.append((yield))
                except _Flush:
                    sink.flush()
            # buffer[-1] contains at least one newline: time to flush!

            # Remove that last item from buffer and split on newlines. Remove
            # any stray '\r' at the end of each piece.
            pieces = [p.rstrip('\r') for p in buffer.pop(-1).split('\n')]
            # Even '\n'.split('\n') generates ['', '']. In general there are
            # three sections in the resulting list:

            # pieces[0] (possibly empty) is the tail end of the partial line
            # we've been accumulating in buffer. Remove it from pieces,
            # assemble the whole line and emit it. Recall that there's no
            # newline in any string in buffer[:-1], because we always flush
            # buffer as soon as buffer[-1] contains a newline.
            sink.write(''.join(buffer + [pieces.pop(0), self.eol]))

            # pieces[-1] (possibly empty) is the fragment at the start of the
            # next partial line. Remove it from pieces and capture in buffer
            # for later.
            # This is where the distinction between splitlines() and
            # split('\n') becomes important. 'abc\n'.splitlines() returns
            # simply ['abc'], while 'abc\n'.split('\n') returns ['abc', ''].
            # The latter is essential if we are to properly handle an item
            # with a dangling partial line fragment.
            buffer = [pieces.pop(-1)]

            # The remaining middle of pieces is the list (possibly empty) of
            # unbroken lines from the most recent (yield) expression. And yes,
            # '\n\n' pairs will send an empty line through sink.write().
            for line in pieces:
                sink.write(line + self.eol)

            # Loop back to accumulate more fragments in buffer.

class overtype(ofilter):
    """
    buffer_lines handles the case when you want a sink (e.g. a logger) to
    process complete lines from the source. overtype handles the further case
    when lines from the source include '\r' characters intended to replace the
    line so far with new content, e.g. for progress output on a console.
    That's great for a watching user, not so great for a log file after the
    fact: you end up with lots of nearly-identical progress lines that detract
    from readability of the log.

    Expected usage would be as a sink for buffer_lines, e.g.:

    outfile = buffer_lines(overtype(adapter(logger.info)))
    """
    def write(self, line):
        # If, as we expect, each write() call passes a complete line
        # (formerly) ending in newline, all we need do is split on '\r'
        # characters and take the last chunk. In fact we need only rsplit()
        # once.
        super(overtype, self).write(line.rsplit('\r', 1)[-1])

class _syslogger(ofilter):
    """
    An instance of this class is a 'file-like object' whose write() method
    writes to syslog.
    """
    def __init__(self, *args, **kwds):
        """
        Constructor accepts syslog.openlog() arguments, plus a keyword-only
        argument level= [default syslog.LOG_INFO] which will be passed to each
        syslog.syslog() call along with the text.
        """
        # remove level= from kwds so openlog() won't crump
        self.level = kwds.pop("level", syslog.LOG_INFO)
        # forward all remaining arguments to openlog()
        syslog.openlog(*args, **kwds)

    def write(self, text, **kwds):
        # Accept an extension keyword-only level= parameter. Unless you
        # override it in this write() call, the default log level is as
        # specified to our constructor.
        syslog.syslog(kwds.pop("level", self.level), text)

    def flush(self):
        pass

def syslogger(*args, **kwds):
    """
    Wrap _syslogger so that we properly buffer lines to go to the log.
    """
    return buffer_lines(_syslogger(*args, **kwds))

logwrappers = namedtuple('logwrappers',
                         ('debug', 'info', 'warning', 'error', 'critical', 'exception'))

def wraplogger(logger):
    """
    Given a logging.Logger instance 'logger', return a logwrappers namedtuple
    whose 'debug' attribute is a file-like object targeting logger.debug(),
    'info' attribute is a file-like object targeting logger.info(), etc. Pick
    whichever ones you want to pass to an API expecting a file-like output
    object.
    """
    # adapter(logger.info) gets us a file-like object targeting logger.info().
    # But since each logger.info() call creates a separate line in the target
    # log file, and since each (e.g.) print() call calls write() on its file
    # argument multiple times to write partial lines and then an eol, wrap the
    # adapter in buffer_lines to map assembled partial lines to single info()
    # calls.
    # We intentionally defined logwrappers fields with the same names as the
    # logger methods we publish.
    return logwrappers(**{ field: buffer_lines(adapter(getattr(logger, field)))
                           for field in logwrappers._fields })

@contextmanager
def log_handler(name, handler, level=None, propagate=None, optional=False):
    """
    Within a 'with log_handler('module', handler):' block, the passed
    'handler' is added to the logger named 'name' ('module' in this example,
    None for the root logger). Optionally pass level as well to temporarily
    override the logger's level.

    You may also pass a logging.Logger instance as 'name' if you happen to
    have one in hand.

    Pass handler=None to engage the other documented behavior without
    saving/restoring the handler.

    'with log_handler('module', handler) as logger:' surfaces the logger
    instance for use within the block.

    Pass propagate=False to hijack any messages sent to this logger ONLY to
    the specified handler, rather than allowing them to propagate to parent
    loggers in the logger hierarchy.

    Pass optional=True to set the specified handler only when there aren't
    already handlers for the selected logger. ('optional' is ignored in Python
    older than 3.7.)
    """
    # Allow passing 'name' as a Logger instance; otherwise look it up.
    logger = name if isinstance(name, logging.Logger) else logging.getLogger(name)

    # Logger.hasHandlers() was introduced in Python 3.2. In older Python, we
    # can't tell, so make hasHandlers() unconditionally return False, which
    # has the effect of ignoring 'optional'.
    hasHandlers = getattr(logger, 'hasHandlers', lambda: False)

    if (not handler) or (optional and hasHandlers()):
        # Skip adding this handler:
        # if handler passed as None
        # or optional and handlers are already set.
        handler = None
    else:
        # Add passed handler if not optional.
        # Add passed handler if optional but there are no existing handlers.
        logger.addHandler(handler)

    prevlevel = logger.level
    if level is not None:
        logger.setLevel(level)

    prevprop = logger.propagate
    if propagate is not None:
        logger.propagate = propagate

    try:
        yield logger
    finally:
        logger.propagate = prevprop
        logger.setLevel(prevlevel)
        if handler:
            # Only if we called addHandler() above.
            logger.removeHandler(handler)

class tee(ofilter):
    """
    tee(stream0, stream1, ...) provides a file-like API that forwards every
    write() and flush() call to each of stream0, stream1, etc., in the order
    passed to the constructor. Naturally stream0, stream1, etc., must provide
    a write(), flush() API as well.
    """
    def __init__(self, *sinks):
        self.sinks = sinks

    def write(self, data):
        for sink in self.sinks:
            sink.write(data)

    def flush(self):
        for sink in self.sinks:
            sink.flush()

# Link JsonLines.handle() onto chain of sys.excepthook handlers
class JsonLines(exceptlink):
    """
    JsonLines is intended to produce a supplemental log file for programmatic
    consumption. The main log file includes all sorts of detail potentially
    interesting to a human reader wondering what happened to the run, but
    attempting to scrape it for statistics is by definition a dicey problem.

    JsonLines appends to a text file, each line of which contains a separate
    serialized JSON object. Each such object contains:

    time:   ISO-format timestamp
    action: started, stopped, starting, finished, aborted, exception
    key:    arbitrary string by which 'starting' and 'finished'/'aborted' can
            be paired

    When instantiated, JsonLines immediately writes a 'started' entry with key
    null. This entry is intended to represent the start of the writer process.
    On termination (as mediated by atexit), JsonLines writes a 'stopped' entry
    with key null. Moreover, on unhandled exception, JsonLines writes an
    'exception' entry whose key is a description of the exception.

    The intention is that a script can read the output file to determine the
    status of the writer process. At startup, the writer instantiates
    JsonLines. It then (perhaps iteratively) performs, inside a 'with
    jsonlines.task(key):' block, the task distinguished by 'key'.
    (Alternatively, the writer may call the starting(key) and finished(key)
    methods, or aborted(key), explicitly.)

    The idea is that the reader should be able to:

    - determine when the oldest run started (timestamp on first 'started'
      entry, of course subject to the user periodically deleting the file)
    - determine when the current run started (timestamp on last 'started'
      entry)
    - determine the number of tasks finished this run (count 'finished'
      entries since last 'started' entry)
    - determine the number of tasks finished overall (count all 'finished'
      entries)
    - determine the average time per task (subtract timestamps for matching
      'finished' and 'starting' keys)
    - determine the number of running tasks ('starting' keys without matching
      'finished' or 'aborted' keys since last 'started' key)
    - determine whether the current run is still going
    - determine whether the current run terminated gracefully or with an
      unhandled exception.

    Especially on a headless AWS system, it is of great interest to know
    whether a long-running process is still making progress, and JsonLines
    tries very hard to expose that. Of course the atexit documentation details
    circumstances in which the interpreter might terminate without calling
    registered atexit functions, but barring those, the output file should
    contain a 'stopped' entry. Moreover, JsonLines hooks sys.excepthook so
    that an unhandled exception should also produce an 'exception' entry. (You
    get both 'exception' and 'stopped', rather than 'exception' replacing
    'stopped'.)

    Even if the writer process hung, or crashed without running atexit
    functions, the alert reader should be able to notice that unfinished tasks
    seem to be taking way longer than the average duration of finished tasks.
    Or possibly the most recently launched tasks all ended with 'aborted', yet
    there's neither a 'stopped' entry nor any new 'starting' entries.

    Why distinct JSON objects, each on a separate line?

    A file intended for script consumption could use any of a number of
    serialization formats: Python's own pprint.pprint() syntax (readable with
    ast.literal_eval()), LLSD, XML, JSON, .ini (or configfile) format, the
    list goes on. But with most of them, you would need to rewrite the entire
    file each time you wanted to add an item to the collection. We want a file
    format compatible with simply appending.

    The simplest text file syntax, directly supported by Python iteration, is
    a sequence of lines delimited by '\n'. That nicely supports a sequence of
    items where each item is a single string.

    It's trickier when each item is a data structure of some kind. One is
    tempted to invent serialization syntax, e.g. 'key=value\n'. But that
    quickly runs into escape requirements...

    We choose to use a well-established serialization format (JSON), but to
    store multiple instances, each on its own text line. We depend on the fact
    that json.dump() introduces no line breaks unless specifically asked. This
    allows the writer to append new entries without rewriting previous ones,
    while permitting the reader a simple but comprehensive parsing scheme: (1)
    read text line, (2) call json.loads().
    """
    def __init__(self, filename, system=False):
        # JsonLines is specifically intended to support a long-running process
        # that may need to be restarted multiple times, perhaps to fix bugs in
        # rarely-hit code. Append to any existing file so that a reader can
        # look further back in history than the current run.
        self.outf = open(filename, "a")
        # don't forget to engage exceptlink.__init__()
        super(JsonLines, self).__init__(system)
        # Of course this isn't literally when the run started, but in typical
        # usage, JsonLines should be instantiated soon after -- and anyway,
        # this is the first chance we get because we've only just opened the
        # file.
        self.write('started', None)
        # Make sure we append to the file when we exit.
        atexit.register(self.write, 'stopped', key=None)

    def handle(self, type, value, traceback):
        # Appending a 'stopped' entry on termination (see __init__()) is
        # great, but was that intentional or because of unhandled exception?
        # This exceptlink.handle() override distinguishes the two cases.
        self.write('exception', key=describe(value))

    @contextmanager
    def task(self, key):
        """
        with jsonlines.task(key):
            # ... some processing ...

        appends a 'starting key' entry on entry to the 'with' block;
        appends a 'finished key' entry on normal exit from the block;
        appends an 'aborted key' entry on exception exit from the block.
        """
        self.starting(key)
        try:
            yield
        except Exception as err:
            self.aborted(key)
            raise
        else:
            self.finished(key)

    def starting(self, key):
        self.write('starting', key)

    def finished(self, key):
        self.write('finished', key)

    def aborted(self, key):
        self.write('aborted', key)

    def write(self, action, key):
        json.dump(dict(time=datetime.datetime.today().isoformat(), action=action, key=key),
                  self.outf)
        self.outf.write('\n')
        self.outf.flush()
