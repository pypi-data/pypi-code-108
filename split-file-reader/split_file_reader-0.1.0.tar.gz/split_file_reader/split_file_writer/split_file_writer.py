# -*- coding: utf-8 -*-
"""
    split_file_writer
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
from abc import ABC, abstractmethod
import io
import os
import typing


class IndexableObject(ABC):  # pragma: no cover
    """
    This class exists strictly for the type hint.  Anything that can have `len()` called on it, and `[]` slicing applied
    to it is acceptable.

    This means a `bytes` or `bytearray` is acceptable.
    """

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __len__(self):
        pass


class SplitFileWriter(io.BytesIO):
    def __init__(
        self,
        filenames: typing.Union[
            os.PathLike,
            str,
            typing.List[typing.Union[os.PathLike, str]],
            typing.Generator[typing.IO, IndexableObject, None],
            None,
        ] = None,
        max_part_size: int = 500_000,
    ):
        """
        Write up to a given number of bytes to an output stream, then move to the next stream.  The generator will
        open & close the streams as it sees fit.  Most commonly for actual files on disk, but may be applied to any
        file-like object.

        `filenames` should be a generator for writable file-like objects.  However, SplitFileWriter can construct this
        generator for you via the following:

        If `filenames` is None, a default generator that works identically to bsd `split` will be created,
        with values of `xaa`, `xab`, `xac`, ... in the current working directory.

        Else, If `filenames` is a single `str` or `PathLike`, a default file generator will be created that simply
        appends a 3 digit numeric value to the end of the filepath.

        Else, If `filenames` is a `list`, the list be assumed to be `str` or `os.PathLike` as described above, and a
        file will be opened for each of element.  No suffix will be added.  If the list is too small, a
        `StopIteration` exception will be raised at the end of the list.

        Else, `filenames` will be assumed to be a Generator, and SplitFileWriter will call `iter()` on it, then
        advance it via `next()`.  This is user supplied, and take any construction you wish, so long as the object it
        yields supports `write()` and `close()`

        When `close()` is called on SplitFileWriter, `close()` will be called on the `file_generator` as well.  This
        ensures the generator is cleaned up immediately and last chunks are written.
        `close()` on a generator will trigger a `StopGeneration` exception to be raised at the `yield` line.  Files
        created by context managers in a loop, then yielded out, will then be closed.  See the Simple generator for an
        easy example
        https://www.python.org/dev/peps/pep-0342/#new-generator-method-close

        :param filenames: A str, PathLike, a list of str or PathLike, or a generator to produce file-like objects.
        :param max_part_size: Max size in bytes for each file chunk; must be a positive integer.
        """
        # Is this output stream closed?  (has `close()` been called on this object?)
        self._closed: bool = False
        # The max file size for a given output part before requesting a new one.
        assert isinstance(max_part_size, int)
        assert max_part_size > 0
        self._max_part_size: int = max_part_size

        # Stored copy of the generator used to open new files.
        # No matter what is passed as an argument, convert it to a generator.
        if isinstance(filenames, os.PathLike):
            filenames = os.fspath(filenames)
        if filenames is None:
            self._file_gen = splitlike_file_generator()
        elif isinstance(filenames, str):
            self._file_gen = counting_file_generator(filenames)
        elif isinstance(filenames, list):
            self._file_gen = file_generator_from_list(filenames)
        else:
            self._file_gen = filenames
        # Currently opened file-like object.
        self._file_ptr = None
        # The tell position, cumulative of every file that has been opened.
        self._told: int = 0
        # An iterable is used to manage the writing, `send()` is used to control the output.
        self._write_iter: typing.Generator[None, IndexableObject, None] = self.__write_generator()
        # Init the iter.
        next(self._write_iter)

    def writable(self) -> bool:
        """
        Always True.
        :return:
        """
        return True

    def write(self, value: IndexableObject) -> int:
        """
        Write anything to the underlying output file.  Must be slicable, and must implement __len__.  `bytes` or
        `bytearray` or `str` are all acceptable.

        :param value:  Object to write.
        :return:  Length of data written.
        """
        if self._closed:
            raise IOError("Outfile is closed.")
        self._write_iter.send(value)
        return len(value)

    def close(self) -> None:
        """
        Close the file.

        Calls `close()` on the `file_generator` as well, to close the file stream.
        :return:
        """
        self._closed = True
        # Generators have a send() _and_ a close().  Also a throw().
        self._write_iter.close()
        self._file_gen.close()

    def flush(self):
        """
        Flushes the output stream.

        Calls `flush` on the current file pointer.  If a `write` spanned multiple file objects, flush will only be
        called on the current file object, it is up to the file generator to ensure that previous files have flushed
        or closed.
        :return:  Whatever the file pointer flush value is.  Usually, None.
        """
        return self._file_ptr.flush()

    def __write_generator(self) -> typing.Generator[None, IndexableObject, None]:
        chunk = None

        # file_gen_iter = iter(self._file_gen)
        # while True:
        for self._file_ptr in iter(self._file_gen):
            part_wrote = 0
            # self._file_ptr = next(file_gen_iter)
            while True:
                if not chunk:
                    chunk = yield
                available = self._max_part_size - part_wrote
                size = self._file_ptr.write(chunk[:available])
                part_wrote += size
                self._told += size
                chunk = chunk[available:]
                if available <= len(chunk):
                    break

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def tellable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._told

    def seekable(self) -> bool:
        return False

    def seek(self, offset: typing.Optional[int] = ..., whence: typing.Optional[int] = ...) -> int:
        raise io.UnsupportedOperation("{} cannot seek.".format(self.__class__.__name__))

    def readable(self) -> bool:
        return False

    def read(self, size: typing.Optional[int] = ...):
        raise io.UnsupportedOperation("{} cannot read.".format(self.__class__.__name__))

    def truncate(self, size: typing.Optional[int] = ...):
        raise io.UnsupportedOperation("{} cannot truncate.".format(self.__class__.__name__))

    def fileno(self) -> int:
        if self._file_ptr:
            return self._file_ptr.fileno()
        raise IOError("No current file descriptor in use.")

    def __repr__(self):
        return "<{cls}, {id}: Tell: {tell}, File Str: {fdesc}>".format(
            cls=self.__class__.__name__, id=hex(id(self)), tell=self.tell(), fdesc=str(self._file_ptr)
        )


def counting_file_generator(filename: str, start_from=0, width=3) -> typing.Generator:
    """
    Its a generator!  Implement at will, but this is a simple file generator, making files in a directory.  Modify this
    to construct your file names as you wish.  When `close()` is called on the `SplitFileWriter`, `close()` will be
    called on this generator as well.

    :param filename:  `path/to/file.bin.`  Include the trailing dot if desired.
    :param start_from:  Numeric index to start from.
    :param width:  Minimum number of numeric digits to append.
    :return:
    """
    idx = start_from
    formatter = "{{}}{{:0{:d}d}}".format(width)
    # "{}{:03d}"
    while True:
        name = formatter.format(filename, idx)
        with open(name, mode="wb") as file_ptr:
            yield file_ptr
        idx += 1


def file_generator_from_list(list_of_filenames: typing.List[str]):
    """
    For a list of filepaths, open a file pointer for writing.

    :param list_of_filenames: A list of str or os.PathLink objects that will be passed to `builtins.open()`
    :return:
    """
    for filename in list_of_filenames:
        if isinstance(filename, os.PathLike):
            filename = os.fspath(filename)
        with open(file=filename, mode="wb") as file_ptr:
            yield file_ptr


def splitlike_file_generator(prefix="x", addl_suffix="") -> typing.Generator:
    """
    `split` default names are weird but alphabetical.  Add the filepath to the prefix to write specific places.
    Filename prefix of `x`, with two letter suffixes from `aa` to `yz`.
    Then, prefix of `xz`, with three letter suffixes from `aaa` to `yzz`.
    Then, prefix of `xzz`, with four letter suffixes from `aaaa` to `yzzz`.
    Every time this loops, add another `z` to the prefix, then add another alphabet term to the counter.
    `xaa`, `xab`, ... `xyy`, `xyz`, `xzaaa`, `xzaab`, ... `xzyzy`, `xzyzz`, `xzzaaaa`, `xzzaaab`

    :param prefix:  Filename prefix, this is the filepath and basename of the file.
    :param addl_suffix:  After the dynamic, incrementing suffix, add this.
    :return:
    """
    import string

    def suffix_gen(letters):
        if len(letters) == 1:
            for letter in letters[0]:
                yield letter
        else:
            for letter in letters[0]:
                for later_letters in suffix_gen(letters[1:]):
                    yield letter + later_letters

    list_of_suffixes = [list(string.ascii_lowercase[:-1])]
    while True:
        list_of_suffixes.append(list(string.ascii_lowercase))
        for suffix in suffix_gen(list_of_suffixes):
            name = "{}{}{}".format(prefix, suffix, addl_suffix)
            with open(name, mode="wb") as file_ptr:
                yield file_ptr
        prefix += "z"
