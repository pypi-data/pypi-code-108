"""
Utility classes and functions for working with aiohttp.
"""

from contextlib import AbstractContextManager
from multiprocessing.connection import Connection
from io import BytesIO
from aiohttp.streams import StreamReader
from typing import Protocol


class AioHTTPFileLikeObjectWrapper:
    """
    Wraps aiohttp.streams.StreamReader.read_nowait in a read() method so that it can be passed where file-like objects
    are expected.
    """
    def __init__(self, reader: StreamReader):
        """
        Creates a new AioHTTPFileLikeObjectManager object, passing in the stream reader to wrap.

        :param reader: a aiohttp.streams.StreamReader (required).
        """
        if reader is None:
            raise ValueError('reader cannot be None')
        self.__reader = reader

    def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        return self.__reader.read_nowait(n)


class ConnectionFileLikeObjectWrapper(AbstractContextManager):
    """
    Wraps a multiprocessing.connection.Connection object and provides file-like object methods.

    This class is a context manager, so it can be used in with statements.
    """
    def __init__(self, conn: Connection):
        """
        Creates a new ConnectionFileLikeObjectWrapper object, passing in the connection to wrap.

        :param conn: a multiprocessing.connection.Connection object (required).
        """
        if conn is None:
            raise ValueError('conn cannot be None')
        self.__conn = conn
        self.__buffer = BytesIO()

    def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        if len(b := self.__buffer.read(n)) > 0:
            return b
        try:
            result: bytes = self.__conn.recv_bytes()
            if len(result) > n:
                pos = self.__buffer.tell()
                self.__buffer.write(result[n:])
                self.__buffer.seek(pos)
                return result[:n]
            else:
                return result
        except EOFError:
            return b''

    def write(self, b):
        """
        Sends some bytes to the connection.

        :param b: some bytes (required).
        """
        self.__conn.send_bytes(b)

    def fileno(self):
        """
        Returns the integer file descriptor that is used by the connection.

        :return: the integer file descriptor.
        """
        return self.__conn.fileno()

    def close(self):
        """
        Closes the connection and any other resources associated with this object.
        """
        try:
            self.__buffer.close()
            self.__conn.close()
            self.__conn = None
        finally:
            if self.__conn is not None:
                try:
                    self.conn.close()
                except OSError:
                    pass

    def __exit__(self, *exc_details):
        self.close()


class SupportsAsyncRead(Protocol):
    """
    Protocol with an async read() method and a close() method.
    """
    async def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        pass

    def close(self):
        """
        Closes any resources associated with this object.
        """
        pass


class AsyncReader:
    """
    Wraps a bytes object in a simple reader with an asynchronous read method and a close method.
    """
    def __init__(self, b: bytes):
        """
        Creates a new AsyncReader, passing in a bytes object.

        :param b: bytes (required).
        """
        self.__b = BytesIO(b)

    async def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        return self.__b.read(n)

    def close(self):
        """
        Closes any resources associated with this object.
        """
        self.__b.close()


class StreamReaderWrapper:
    """
    Wraps an aiohttp StreamReader in an asyncio StreamReader-like object with a read() method and a no-op close()
    method.
    """
    def __init__(self, reader: StreamReader):
        if reader is None:
            raise ValueError('reader cannot be None')
        self.__reader = reader

    async def read(self, n=-1):
        """
        Reads up to n bytes. If n is not provided, or set to -1, reads until EOF and returns all read bytes.

        If the EOF was received and the internal buffer is empty, returns an empty bytes object.

        :param n: how many bytes to read, -1 for the whole stream.
        :return: the data.
        """
        return await self.__reader.read(n)

    def close(self):
        pass
