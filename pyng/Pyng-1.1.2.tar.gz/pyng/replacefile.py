#!/usr/bin/python
"""\
@file   replacefile.py
@author Nat Goodspeed
@date   2011-04-13
@brief  In-place text-file replacement

Copyright (c) 2011, Nat Goodspeed
"""

import os
import errno
import shutil
import sys
import tempfile

if sys.version_info[0] >= 3:
    # NamedTemporaryFile(buffering=)
    _bufparam = 'buffering'
else:
    # NamedTemporaryFile(bufsize=)
    _bufparam = 'bufsize'

class ReplaceFile(object):
    """
    ReplaceFile is a ContextManager to assist in filtering and replacing a
    text file in place.

    Use like this:

    with ReplaceFile("somefile.txt") as (inf, outf):
        for line in inf:
            outf.write(line)

    When you exit the 'with' statement, "somefile.txt" is closed and replaced.
    If the body of the 'with' statement raises an exception, "somefile.txt" is
    retained as-is; its would-be replacement is discarded.

    The fileinput library module has partial support for this, but it's not
    general: you can't append to the original file without switching paradigms.
    Consider:

    import sys, fileinput
    for line in fileinput.input("somefile.txt", inplace=True):
        sys.stdout.write(line)
    sys.stdout.write("one more line\n")

    Unfortunately, "somefile.txt" is closed and replaced when the 'for' loop
    reaches EOF, and "one more line\n" is sent to the original stdout.

    Another gripe: hijacking sys.stdout means you have to be very careful with
    informational output produced by any called code. (Also, it makes
    interactive testing a bear.)
    """
    def __init__(self, filename, inmode="r", outmode="w", newext=None, oldext=None):
        """
        Pass:

        filename is the name of an existing text file. If it doesn't exist,
        you'll get the exception raised by open(filename, inmode). If it's not
        in a writable directory, or not on a writable filesystem, you'll get
        the exception raised by open(filename, outmode).

        inmode is the open() mode for the input file, default "r".

        outmode is the open() mode for the output file, default "w".

        newext is the extension to append to filename for the new temporary
        file before replacement, e.g. ".new". If you specify this and the body
        of the 'with' statement raises an exception, the temporary file
        (filename + newext) is preserved for your inspection. If you omit
        newext, the temporary file is given an arbitrary name, and is deleted
        on exception.

        oldext is the extension to append to filename to keep the original
        file contents after replacement, e.g. ".bak". If you specify this and
        the 'with' statement leaves normally, the original file is renamed to
        (filename + oldext). If you omit oldext, normally the original file is
        deleted. However, on exception, oldext is moot because the original
        file is retained.
        """
        self.filename = filename
        self.inmode = inmode
        self.outmode = outmode
        self.newext = newext
        self.oldext = oldext
        # Don't do anything with any of these yet. This addresses the
        # (admittedly peculiar) use case of writing something like:
        # repf = ReplaceFile("somefile.txt")
        # for input in somesequence:
        #    with repf as (inf, outf):
        #        ...
        self.outname = None
        self.inf = None
        self.outf = None

    def __enter__(self):
        # We always just open self.filename with self.inmode.
        self.inf = open(self.filename, self.inmode)
        # How we open the temp output file depends on newext.
        if self.newext:
            # Caller wants a predictable name, preserved on exception.
            # Construct the name, and open it the obvious way.
            self.outname = self.filename + self.newext
            self.outf = open(self.outname, self.outmode)
        else:
            # Caller is fine with an arbitrary name, destroyed on exception.
            # Use NamedTemporaryFile. By default such files are unbuffered; we
            # want to buffer it like a normal disk file. (How to find out
            # default buffer size?) We don't care what the name is -- but we
            # DO insist that it be placed in the same directory as
            # self.filename: if that dir isn't writable, we need to know now.
            self.outf = tempfile.NamedTemporaryFile(mode=self.outmode,
                                                    dir=os.path.dirname(self.filename),
                                                    delete=False,
                                                    **{ _bufparam: 16*1024 })
            self.outname = self.outf.name
        return self.inf, self.outf

    def __exit__(self, type, value, tb):
        self.inf.close()
        self.outf.close()

        if type or value or tb:
            # Leaving via exception. Unconditionally preserve self.filename.
            # But unless caller specified newext, remove self.outname.
            if not self.newext:
                os.remove(self.outname)
            return False                # propagate exception

        # Here we're leaving the 'with' statement normally: no exception. That
        # "commits" changes to self.filename.

        # We may have opened outname using NamedTemporaryFile, which
        # explicitly restricts the permission bits on the new file. Now that
        # we intend to commit the replacement, though, ensure new file has the
        # same mode bits as the original.
        shutil.copymode(self.filename, self.outname)

        if self.oldext:
            # Caller wants to preserve original file.
            oldname = self.filename + self.oldext
            # Get rid of any earlier backup file that would collide with
            # oldname.
            try:
                os.remove(oldname)
            except OSError as err:
                if err.errno != errno.ENOENT:
                    # If the remove() error isn't nonexistence, holler about it.
                    raise
            # Rename original file.
            os.rename(self.filename, oldname)

        else:
            # Caller omitted oldext: s/he doesn't need original file
            # preserved.
            os.remove(self.filename)

        # Either way, new file now replaces original file.
        os.rename(self.outname, self.filename)
