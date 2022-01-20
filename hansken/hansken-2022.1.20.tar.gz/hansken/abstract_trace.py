from abc import ABC, abstractmethod

from hansken.util import DictView


class AbstractTrace(ABC, DictView):
    @abstractmethod
    def update(self, key_or_updates=None, value=None, data=None, overwrite=False):
        """
        Requests the remote to update or add metadata properties for this
        `.Trace`.

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

    @abstractmethod
    def open(self, stream='raw', offset=0, size=None):
        """
        Open a data stream of a named stream (default ``raw``) for this
        `.Trace`.

        .. note::
            Multiple calls to `read(num_bytes)` on the stream resulting from
            this call works fine in Python 3, but will fail in Python 2.

        :param stream: stream to read
        :param offset: byte offset to start the stream on
        :param size: the number of bytes to make available
        :return: a file-like object to read bytes from the named stream
        :rtype: `io.BufferedReader`
        """

    @abstractmethod
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
