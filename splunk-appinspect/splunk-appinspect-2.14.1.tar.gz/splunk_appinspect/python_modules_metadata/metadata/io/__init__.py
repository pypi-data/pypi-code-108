"""
The io module provides the Python interfaces to stream handling. Under Python 2.x,
this is proposed as an alternative to the built-in file object,
but in Python 3.x it is the default interface to access files and streams.
"""
from splunk_appinspect.python_analyzer.ast_types import AstVariable
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_consts import (
    TagConsts,
)
from splunk_appinspect.python_modules_metadata.metadata_common.metadata_decorator import (
    executable,
    tags,
)


@tags(TagConsts.FILE_READ_AND_WRITE)
@executable
def open(args, keywords, **kwargs):
    """
    Open file and return a corresponding stream.
    """
    return AstVariable(None, {"file"})


class FileIO:
    """
    FileIO represents an OS-level file containing bytes data.
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """
        Read data from underlying object
        :return:
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        Write data to the underlying stream
        """
        pass


class BytesIO:
    """
    Buffered I/O streams provide a higher-level interface to an I/O device than raw I/O does.
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """
        Read data from underlying object
        :return:
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        Write data to the underlying stream
        """
        pass


class BufferedReader:
    """
    A buffer providing higher-level access to a readable, sequential RawIOBase object
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """
        Read data from underlying object
        :return:
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        Write data to the underlying stream
        """
        pass


class BufferedWriter:
    """
    A buffer providing higher-level access to a writeable, sequential RawIOBase object.
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """
        Read data from underlying object
        :return:
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        Write data to the underlying stream
        """
        pass


class BufferedRandom:
    """
    A buffered interface to random access streams.
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """
        Read data from underlying object
        :return:
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        Write data to the underlying stream
        """
        pass


class TextIOWrapper:
    """
    A buffered text stream over a BufferedIOBase binary stream
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """
        Read data from underlying object
        :return:
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        Write data to the underlying stream
        """
        pass


class BufferedRWPair:
    """
    A buffered I/O object combining two unidirectional RawIOBase objects
    into a single bidirectional endpoint
    """

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def read(self):
        """
        Read data from underlying object
        :return:
        """
        pass

    @tags(TagConsts.FILE_READ_AND_WRITE)
    def write(self):
        """
        Write data to the underlying stream
        """
        pass
