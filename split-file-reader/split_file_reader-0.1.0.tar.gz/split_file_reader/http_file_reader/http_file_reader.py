# -*- coding: utf-8 -*-
"""
    http_file_reader
    Copyright (C) 2022  Xavier Halloran, United States

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import logging
import typing
import io
import json

import requests

logger = logging.getLogger(__name__)


def trace(val, *args, **kwargs):
    logger.log(logging.DEBUG - 5, val, *args, **kwargs)


def debug(val, *args, **kwargs):
    logger.log(logging.DEBUG, val, *args, **kwargs)


class HTTPFileReader(io.BytesIO):
    """
    Acts file-like for files hosted on an HTTP server readably in binary mode.
    Provides `readable`, `writable`, `seekable`, `tellable`.
    Implements `read`, `readinto`, `seek`, `tell`
    Prohibits `write`, `writelines`, readline`, `readlines`, `truncate`
    Also implements `open`, `close`, `closed`, `__repr__`, `__enter__`, and `__exit__`

    This class can be used directly with ZipFile or TarFile, as follows:

    with requests.Session() as session:
        with HTTPFileReader(url="https://gitlab.com/files.zip?inline=false", session=session) as hfr:
            with zipfile.ZipFile(file=hfr, mode="r") as zf:

    with requests.Session() as session:
        with HTTPFileReader(url="https://gitlab.com/files.tar?inline=false", session=session) as hfr:
            with tarfile.open(fileobj=hfr, mode="r") as tf:

    `close` takes no real action.  The requests.Session is managed externally, and there is no file descriptor or
    buffer.

    Ranged queries return `206 Partial Content`.
    Invalid ranges return `416 Range Not Satisfiable`.
    If the service does not process Ranged data, it returns `200 OK` and presents the entire document.
    Dynamic values of the target file may not be supported.
    Dynamic values of the URL parameters or headers are not supported.
    github and gitlab both support Ranged queries for git project files.

    This class is not thread-safe; no method is idempotent, all of them affect the object state.  However, since the
    underlying files are all read-only, multiple concurrent instances of this class is allowed.
    """

    def __init__(
        self,
        url: str,
        session: typing.Optional[requests.Session],
        mode: str = "rb",
        headers: typing.Optional[typing.Dict] = None,
        raise_for_status: bool = False,
    ) -> None:
        """
        Open an HTTP connection to a remote server, query the file size, and begin random-accessing it.  Ideal for TAR
        or ZIP files.

        The HTTP server must support "Range" header options, and reliable HEAD options.

        :param url: File target URL.
        :param mode: Must be "r"/"rb", kept only as a parameter to support libraries that expect to set it.
        :param session: A user-supplied requests.Session object.
        :param headers: Headers to accompany the HTTP traffic.  Not required, `Range` will be overwritten.
        :param raise_for_status: Call the `requests.response.raise_for_status` method to ensure safe HTTP response.
        """

        if mode not in ["rb", "br", "r"]:
            # On Unix, "r" and "rb" are the same.  On windows, "r" will alter line endings.
            raise ValueError("mode must be 'rb', was {}".format(mode))
        self.url: str = url
        # The user-supplied the session object
        self._session: requests.Session = session
        # Possible user-supplied headers.
        self._headers: typing.Dict = headers or {}
        # Max file size, the EOF byte, according to the `Content-Length` in a HEAD request.
        self._size: int = 0
        # Value that `tell()` responds with.
        self._told: int = 0

        self.raise_for_status = raise_for_status

        res = self._session.head(self.url, headers=self._headers)
        # print(json.dumps(dict(res.headers), indent='\t'))
        if self.raise_for_status:
            res.raise_for_status()
        try:
            self._size = int(res.headers.get("Content-Length"))
        except TypeError:
            raise ValueError("URL failed to return a valid Content-Length: {}".format(self.url))
        debug("File target_size: {}".format(self._size))

    def readable(self) -> bool:
        return True

    def read(self, target_size: typing.Optional[int] = None) -> typing.AnyStr:
        """
        Read the specified amount, making underlying file boundaries invisible to the caller.

        If the current file pointer has been set to None, indicating an earlier call to `close()`, raises IOError.

        May make multiple system calls, but only one to each File Descriptor.

        :param target_size: Expected read size, or -1 or None to read to end.
        :return: bytes-like list, between zero and `target_size` in length.
        """
        debug("Reading {}, currently {}".format(target_size, self._told))
        if target_size and target_size > 0:
            range_start = self._told
            range_end = self._told + target_size - 1
        else:
            range_start = self._told
            range_end = self._size

        headers = self._headers.copy()
        headers.update({"Range": "bytes={}-{}".format(range_start, range_end)})
        res = self._session.get(url=self.url, headers=headers)
        if self.raise_for_status:
            res.raise_for_status()
        # print_xxd_dump(res.content)
        self._told += len(res.content)
        debug("Read {}, currently {}".format(len(res.content), self._told))
        return res.content

    def readinto(self, buffer: bytearray) -> typing.Optional[int]:
        """
        This is the copy/paste implementation of `io.FileIO.readinto()`
        :param buffer:
        :return:
        """
        data = self.read(len(buffer))
        n = len(data)
        buffer[:n] = data
        return n

    def seekable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        debug("Seeking {} Whence {}, currently {}".format(offset, whence, self._told))
        if whence == 0:
            self._told = 0
        elif whence == 2:
            self._told = self._size
        self._told += offset
        # Can't seek off the end.  This will support SplitFilelikeReader and avoid weird HTTP errors.
        self._told = min(self._told, self._size)
        debug("Sought {} Whence {}, currently {}".format(offset, whence, self._told))
        return self._told

    def tellable(self) -> bool:
        return True

    def tell(self) -> int:
        """
        Logically identical to tell() on any other file-like object.

        Returns the offset as a sum of all previous file sizes, plus current file tell()
        :return:
        """
        return self._told

    @classmethod
    def open(cls, *args, **kwargs):
        """
        Wraps the init constructor.

        :param args:
        :param kwargs:
        :return: Newly created SplitFileReader object.
        """
        return cls(*args, **kwargs)

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return "<{cls}, {id}: Tell: {tell}>".format(cls=self.__class__.__name__, id=hex(id(self)), tell=self.tell())

    """
    The following methods exist to support the io.RawIO behavior, and mostly disables their use.

    This permits the HTTPFileReader to work within a context that expects the io.IOBase capabilities, such as a 
    TextIOWrapper
    """

    def writable(self) -> bool:
        return False

    def write(self, b: typing.Union[bytes, bytearray]) -> typing.Optional[int]:
        """
        No writing allowed with this class.
        :param b:
        :return:
        """
        raise io.UnsupportedOperation("{} cannot write.".format(self.__class__.__name__))

    def writelines(self, lines: typing.Iterable[typing.Union[bytes, bytearray]]) -> None:
        """
        No writing allowed with this class.
        :param lines:
        :return:
        """
        raise io.UnsupportedOperation("{} cannot write.".format(self.__class__.__name__))

    def truncate(self, size: typing.Optional[int] = ...) -> int:
        """
        No writing allowed with this class.
        :param size:
        :return:
        """
        raise io.UnsupportedOperation("{} cannot truncate.".format(self.__class__.__name__))

    def isatty(self) -> bool:
        """
        Definitely cannot be a TTY.
        :return:
        """
        return False

    def flush(self) -> None:
        """
        No writing allowed with this class.
        :return:
        """
        pass

    def fileno(self) -> int:
        raise IOError("No current file descriptor in use.")

    def readline(self, size: int = ...) -> bytes:
        raise io.UnsupportedOperation(
            "{} cannot decode text, and therefore cannot readline.".format(self.__class__.__name__)
        )

    def readlines(self, hint: int = ...) -> typing.List[bytes]:
        raise io.UnsupportedOperation(
            "{} cannot decode text, and therefore cannot readlines.".format(self.__class__.__name__)
        )
