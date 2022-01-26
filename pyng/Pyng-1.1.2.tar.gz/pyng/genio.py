#!/usr/bin/python
"""
    genio.py                         Nat Goodspeed
    Copyright (C) 2010               Nat Goodspeed

Streamwise (generator) file I/O, to facilitate filtering by composition

NRG 12/01/10
"""

def filesource(filename, mode="r"):
    """This is a generator that produces every line of the specified
    file. It's essentially the same as iterating over open(filename [, mode]);
    the major difference is that filesource() pointedly closes the file
    immediately when it's exhausted. Using open(filename) assures us that the
    file will eventually be closed, but doesn't give us any clear sense of
    when.
    """
    f = file(filename, mode)
    for ln in f:
        yield ln
    f.close()

def readlines(file):
    """This is a generator that produces every line of the passed file object
    using readline(). The difference between using readlines() and simply
    iterating over the file object is that the latter fills a hidden buffer
    from which it dispenses its lines. readlines() makes individual calls to
    the file object's readline() method to retrieve exactly one line at a
    time. This matters when reading output from a subprocess; readlines()
    displays that output in something approaching real time, whereas iterating
    over the file object waits to fill its buffer before displaying any
    output. The more slowly the subprocess produces output, the more
    exasperating the buffer delay.
    """
    # readline() returns the empty string at EOF.
    line = file.readline()
    while line:
        yield line
        line = file.readline()

def filebufsource(filename, size=16*1024, mode="rb"):
    """Generator for binary files, or for fast bytewise copying of arbitrary
    files. Where filesource uses Python's line parsing, this simply fetches a
    sequence of fixed-size buffers. (Of course the last one is likely to be
    short.) No parsing is required.
    """
    f = file(filename, mode)
    while True:
        # try for the next bufferload
        buf = f.read(size)
        # when we've reached EOF, break the loop
        if not buf:
            break
        # otherwise produce this bufferload and loop back
        yield buf
    f.close()

def filesink(filename, iterable, mode="w", eol=None, flush=False):
    """Write the items from the specified iterable to the named file using its
    writelines() method. Essentially, filesink opens the target file and
    closes it when done.

    Usage would be something like this (copy every line from fileA to fileB):

    filesink("fileB", filesource("fileA"))

    This is essentially a succinct way of writing:

    dest = open("fileB", "w")
    dest.writelines(open("fileA"))
    dest.close()

    You get the streaming behavior -- you don't have to buffer all of fileA in
    memory -- plus you get a try/finally guarantee that fileB will be closed
    when you're done.

    Of course a nice benefit of writing things this way, versus an explicit
    for loop, is that you can toss in filter generators along the way by
    simple composition.

    If you pass eol other than None, every item from the iterable is suffixed
    by an instance of that value. Typical use would be eol="\n" if you want
    each item on a separate line of the output file but don't already have
    '\n' characters on each item.

    If you pass flush=True, we iterate explicitly over write() calls, with
    flush() calls between each one. This can be useful for copying with a
    progress bar, where buffering can seriously confuse the estimate to
    completion.
    """
    if eol is not None:
        # We effect this by interleaving eol values with the iterable items.
        # Recur to pass a modified iterable.
        return filesink(filename, interleave(iterable, itertools.repeat(eol)),
                        mode=mode, eol=None, flush=flush)

    # When we get to this point, eol is definitely None. Any eol requirements
    # are now being dealt with by our iterable.
    f = file(filename, mode)
    try:
        if not flush:
            f.writelines(iterable)
        else:
            for item in iterable:
                f.write(item)
                f.flush()
    finally:
        f.close()
