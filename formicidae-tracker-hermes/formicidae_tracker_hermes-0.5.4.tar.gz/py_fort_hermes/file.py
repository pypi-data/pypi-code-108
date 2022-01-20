"""This module provides a Context to read sequences of tracking file.

Through the file.open() function one can get a context to read hermes
tracking data file sequences.

Example:
   .. code-block:: python

        import py_fort_hermes as fh

        with fh.file.open('tracking.0000.hermes') as f:
            try:
                for ro in f:
                    #do something with ro
            except fh.UnexpectedEndOfFileSequence as e:
                print("%s is corrupted"%e.segmentPath)

"""

import py_fort_hermes as fh
from py_fort_hermes import utils, check

import os
import gzip
import builtins


class Context:
    """
    A context manager class to open a sequence of hermes tracking file.

    It is an iterable to be used in a for loop.

    """
    __slots__ = [
        'width', 'height', 'path', 'followFile', 'filestream', '_line',
        'allocateNewMessages'
    ]

    def __init__(self, filepath, followFile=True, allocateNewMessages=False):
        """Initializes a new Context

        Args:
            filepath (str): the first segment in the sequence to open
            followFile (bool): if False, will stop at the end of filepath,
                otherwise it will try to follow the file sequence
                until the last.
            allocateNewMessages (bool): if True, each call to `next` will
                allocate a new FrameReadout, which will lead to
                performance losses. Otherwise the same object will be
                used and returned.

        """

        self.followFile = followFile
        self.width = 0
        self.height = 0
        self.path = ''
        self._line = fh.Header_pb2.FileLine()
        self._openFile(filepath)
        self.allocateNewMessages = allocateNewMessages

    def __enter__(self):
        return self

    def close(self):
        """
        Closes the context manager manually
        """
        if self.filestream is not None:
            self.filestream.close()
        self.filestream = None

    def __iter__(self):
        return self

    def __next__(self):
        """
        Gets the next readout in the file sequence

        Returns:
            FrameReadout: the next frame readout

        Raises:
            StopIteration: when the last frame in the sequence was
                successfully raise
            UnexpectedEndOfFileSequence: if any error occurs before
                the last file in the sequence is successfully read

        """
        if self.filestream is None:
            raise StopIteration
        self._line.Clear()
        try:
            self._readMessage(self._line)
        except Exception as e:
            raise fh.UnexpectedEndOfFileSequence(
                segmentPath=self.path, what="cannot decode line: %s" % e)
        if self._line.HasField('readout'):
            self._line.readout.width = self.width
            self._line.readout.height = self.height
            if self.allocateNewMessages is True:
                ro = fh.FrameReadout()
                ro.CopyFrom(self._line.readout)
                return ro
            else:
                return self._line.readout
        elif not self._line.HasField('footer'):
            raise fh.UnexpectedEndOfFileSequence(segmentPath=self.path,
                                                 what="got an empty line")

        if self._line.footer.next == '' or not self.followFile:
            self.close()
            raise StopIteration

        newPath = os.path.join(os.path.dirname(self.path),
                               self._line.footer.next)
        self._openFile(newPath)
        return self.__next__()

    def __exit__(self, type, value, traceback):
        self.close()

    def _openFile(self, filepath):
        try:
            self.filestream = builtins.open(filepath + "unc", "rb")
        except Exception:
            self.filestream = gzip.open(filepath)

        h = fh.Header()
        try:
            self._readMessage(h)
        except Exception as e:
            raise fh.InternalError(fh.ErrorCode.FH_STREAM_NO_HEADER,
                                   "cannot parse header: %s" % e.message)

        check.CheckFileHeader(h)
        self.width = h.width
        self.height = h.height
        self.path = filepath

    def _readMessage(self, message):
        size = utils._decodeVaruint32(self.filestream)
        message.ParseFromString(self.filestream.read(size))


def open(filepath, followFile=True, allocateNewMessages=False):
    """Opens a sequence of hermes tracking file.

    Args:
        filepath : a path-like object to open
        followFile (bool): if True the sequence will be read until the
            last file, otherwise only filepath is read
        allocateNewMessages (bool): if True each call to next() will
            return a new FrameReadout. Otherwise, the same object will
            be Clear() and returned.
    Returns:
        Context: a context manager which is iterable
    """
    return Context(filepath, followFile, allocateNewMessages)
