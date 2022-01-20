# -*- coding: utf-8 -*-
"""
    split_file_reader
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
import os
import typing
import io

logger = logging.getLogger(__name__)


def trace(val, *args, **kwargs):
    logger.log(logging.DEBUG - 5, val, *args, **kwargs)


def debug(val, *args, **kwargs):
    logger.log(logging.DEBUG, val, *args, **kwargs)


# The generator has a need to know file direction to set the pointer correctly.
_BACKWARD = -1
_STATIONARY = 0
_FORWARD = 1


class SplitFileReader(io.BytesIO):
    """
    Acts file-like for a list of files opened readably in binary mode.
    Provides `readable`, `writable`, `seekable`, `tellable`.
    Implements `read`, `readinto`, `seek`, `tell`
    Prohibits `write`, `writelines`, readline`, `readlines`, `truncate`
    Also implements `open`, `close`, `closed`, `__repr__`, `__iter__` and `__next__`., `__enter__`, and `__exit__`

    This library makes use of multiple file objects.  Unlike the io.IOBase specs, this class can make multiple system
    calls for any given `seek` or `read` call; therefore it does not extend the io.IOBase Abstract Base Class.  This
    class cannot write.

    This class can be used directly with ZipFile or TarFile, as follows:

    with SplitFileReader([zip_files]) as sfr:
        with zipfile.ZipFile(sfr, mode="r") as zf:

    with SplitFileReader([tar_files]) as sfr:
        with tarfile.open(fileobj=sfr, mode="r") as tf:

    There is no actual enforcement of integrity of the `files` list, one could swap out names other than the
    currently open file.  The list order is important, and it must be indexable.  The entries in `files` do not
    need to be unique.

    `close` must be called just like any other file, or a single file descriptor may be left open.  Making use of the
    context managed approach will take care of that as well.  If str or path-like values are passed, they will be closed
    automatically; but if file-like objects are passed, they will not be closed, manage those objects externally with
    their own context managers.

    This class is not thread-safe; no method is idempotent, all of them affect the object state.  However, since the
    underlying files are all read-only, multiple concurrent instances of this class, attached to the same underlying
    files, is allowed.
    """

    def __init__(
        self,
        files: typing.List[typing.Union[str, os.PathLike, typing.Any]],
        mode: str = "rb",
        stream_only: bool = False,
        validate_all_readable: bool = False,
        iter_size: int = 1,
    ) -> None:
        """
        Creates the file-like object around a series of files.  At return, there will be a single open file descriptor,
        on the first file in the list.

        `files` may be any of os.PathLike, a `str` or any `file-like` object available.  If it is a `str` or `PathLike`
        a new `open()` will be called with that value as a parameter in a context manager.  Otherwise, the file-like
        will have `seek`, `tell`, and `read` called on it directly.  Any mix of types is allowed in the list.

        :param files: List (or indexable collection) of filepaths or file-like objects for opening, reading, and closing
        :param mode: Must be "r"/"rb", kept only as a parameter to support libraries that expect to set it.
        :param stream_only: Determines if Seek will work.  Will be set if iter() is called at any point.
        :param validate_all_readable: Seek over every component file, make sure they can all be read.  This is a
                coherency check that all the files are adequately specified before being the read operations.
        :param iter_size: The size of the data returned by a next() call to this object.  This is typically 1, but may
                be any positive integer.  A value of zero will read the entire file on the next call.
        """
        if mode not in ["rb", "br", "r"]:
            # On Unix, "r" and "rb" are the same.  On windows, "r" will alter line endings.
            raise ValueError("mode must be 'rb', was {}".format(mode))
        if stream_only and validate_all_readable:
            raise ValueError("`stream_only` and `validate_all_readable` cannot both be set.")
        # Need to track a list of files, in order, to concat.  Must be random-accessible.
        self._files = files
        # When using this class as an iterable, or if attached to some sort of streaming output systems, set this to
        # prevent seeking.  tarfile stream reading blocks seek on its own, this is not a requirement for that.
        self._stream_only = stream_only
        # Only applicable to using this object as an iterable.  On next(), this is the length applied to the read()
        # function.  This can be set at any time between read/__next__ calls.
        self._iter_size = iter_size

        # index of where in the `files` list to currently process.  Starts at -1, to allow the generator to advance
        # into the first file immediately.
        self._current_file_desc_idx = 0
        # Create the generator function to move through the list.
        self._file_desc_generator = self._generate_next_file(_STATIONARY)
        # Init the file pointer, and open a true file pointer to an underlying file-like object.
        self._current_file_desc = next(self._file_desc_generator)

        # Value that `tell()` responds with.
        self._told = 0

        if validate_all_readable:
            self.test_all_readable()

    def readable(self) -> bool:
        return True

    def readall(self) -> bytes:
        """
        Wraps `read(-1)`
        :return:
        """
        return self._read(-1)

    def read(self, size: typing.Optional[int] = None) -> typing.AnyStr:
        """
        Read the specified amount, making underlying file boundaries invisible to the caller.

        If the current file pointer has been set to None, indicating an earlier call to `close()`, raises IOError.

        May make multiple system calls, but only one to each File Descriptor.

        :param size: Expected read size, or -1 or None to read to end.
        :return: bytes-like list, between zero and `target_size` in length.
        """
        if size is None or size < 0:
            return self.readall()
        else:
            return self._read(size)

    def _read(self, target_size: int):
        """
        TODO: Make read() call readinto(), instead of the other way around, to support memory-optimized operations.

        :param target_size: Expected read size, or -1 to read to end.
        :return: bytes-like list, between zero and `target_size` in length.
        """
        debug("Reading {}, currently {}".format(target_size, self._told))
        if not self._current_file_desc:
            raise IOError("SplitFileReader is closed.")
        if target_size >= 0:
            # file.read() may return zero-length data, even if only 1 byte is requested and there is actually more data.
            # This is because the end of a single file may have been reached, and more files need to be opened.
            ret = self._current_file_desc.read(target_size)
            remaining = target_size - len(ret)
            # Reads less than the total size are indicative that the end of a file has been reached, and the next one
            # should be cycled in.
            while remaining > 0:
                if not self._safe_advance_file_desc(_FORWARD):
                    # More requested to be read, but there are no more files to open.
                    break
                read = self._current_file_desc.read(remaining)
                remaining -= len(read)
                ret += read
            self._told += len(ret)
        else:
            # Read -1/None behaves differently.
            ret = self._current_file_desc.read(target_size)
            while self._safe_advance_file_desc(_FORWARD):
                read = self._current_file_desc.read(target_size)
                ret += read
            self._told += len(ret)
        debug("Read {}, currently {}".format(len(ret), self._told))
        return ret

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
        return not self._stream_only

    def seek(self, offset: int, whence: int = 0) -> int:
        """
        Move the file pointer along a file.  May advance over zero or more actual files.

        POSIX allows to seek before or after the end of a file, even in read-only mode.  `seek()` before the start of
        the first file will fail; `seek()` beyond the end of the last file is fine.

        If the current file pointer has been set to None, indicating an earlier call to `close()`, raises IOError.

        If the net action of a seek() will move nowhere, no seek call is passed to the underlying file descriptor.
        Some tools, like `zipfile.ZipFile` after a `read()`, will cause a `seek()` to the end of the read location.
        This is a redundant call, with no net movement, but can make network disk based seeks very expensive, especially
        for large numbers of large files, so does nothing here.

        `os.SEEK_SET`, `os.SEEK_CUR`, and `os.SEEK_END` are whence 0, 1, and 2, respectively.  `os.SEEK_HOLE` and
        `os.SEEK_DATA` are not supported.

        :param offset: Byte count to move, relative to `whence`
        :param whence: 0 from start, 1 from current, 2 from end; or os.SEEK_SET, os.SEEK_CUR, os.SEEK_END, respectively.
        :return: The new absolute position, equal to `tell()`
        """

        debug("Seeking {} Whence {}, currently {}".format(offset, whence, self._told))

        if self._stream_only:
            raise IOError("Seek performed on a streaming file.")

        if not self._current_file_desc:
            raise IOError("SplitFileReader is closed.")

        if whence == 0:
            # From the start
            # Do not always immediately `_seek_to_head`, and then scan forward the offset.  There are many libraries
            # out there that make excessive use of `seek(x, 0)` when either `seek(x, 1) or even `seek(0, 1)` would be
            # more reasonable.  zipfile is one such library, making use of one `seek(x, 2)`, and then exclusively
            # `seek(x, 0)`
            how_far_to_go = -(self._told - offset)
            trace("How far to go: {}".format(how_far_to_go))
            if offset == 0:
                # A `seek(0, 0)` is just a shortcut to `_seek_to_head`
                self._seek_to_head()
            elif how_far_to_go == 0:
                trace("Nowhere to go.")
                pass
            elif how_far_to_go > 0:
                self._scan_forward(how_far_to_go)
            elif how_far_to_go < 0:
                self._scan_backward(how_far_to_go)

        elif whence == 1:
            # From the current position
            how_far_to_go = offset
            trace("How far to go: {}".format(how_far_to_go))
            if how_far_to_go == 0:
                trace("Nowhere to go.")
            elif how_far_to_go > 0:
                self._scan_forward(how_far_to_go)
            elif how_far_to_go < 0:
                self._scan_backward(how_far_to_go)

        elif whence == 2:
            # From the end.
            how_far_to_go = offset
            trace("How far to go: {}".format(how_far_to_go))
            # Without a-priori knowledge of the total file sizes, we can't really calculate the offset to go.
            # So, zip all thw way to the end, then navigate as appropriate.
            self._seek_to_tail()
            if how_far_to_go == 0:
                trace("Nowhere to go.")
                pass
            elif how_far_to_go < 0:
                self._scan_backward(offset)
            elif how_far_to_go > 0:
                self._scan_forward(how_far_to_go)

        else:
            raise IndexError("Whence must be 0, 1, or 2")
        debug("Sought {} Whence {}, currently {}".format(offset, whence, self._told))
        return self.tell()

    def _scan_forward(self, offset: int) -> None:
        """
        Forward seeking is tricky; it is posisble to seek beyond the end of a file, even in read-only mode.  So seek
        immediately to the end of the current file descriptor, and check the distance moved.  If moved too far, back up
        to the correct position.  If moved not far enough, go to the next file descriptor, and try again.
        :param offset:
        :return:
        """
        remaining = offset
        while remaining > 0:
            trace("Scanning forward.  Offset: {}, Remaining: {}".format(offset, remaining))
            start_pos = self._current_file_desc.tell()
            # Go all the way to the _end_ of file explicitly, because it is  allowed to seek() beyond that and get
            # misleading tell() information.
            self._current_file_desc.seek(0, 2)
            # Track the actual net movement.
            end_pos = self._current_file_desc.tell()
            moved = end_pos - start_pos
            # Did the seek to the end of the file go too far?
            if moved > remaining:
                # Overshot the seek forward.  Move backward again.
                corrective_move = remaining - moved
                self._current_file_desc.seek(corrective_move, 1)
                end_pos = self._current_file_desc.tell()
                moved = end_pos - start_pos
                # It moved backwards, but `moved` is still positive, because it holds the net movement in this loop.
                self._told += moved
                remaining = 0
            # Did the seek to the end of the file not go far enough?
            else:
                remaining -= moved
                self._told += moved
                # The generator for advancing file descriptors will ensure the pointer is at the start of the file part
                if not self._safe_advance_file_desc(_FORWARD):
                    break
        trace(
            "Out of loop.  Tell: {}  File tell {}:  Current file idx: {}".format(
                self._told, self._current_file_desc.tell(), self._current_file_desc_idx
            )
        )

    def _scan_backward(self, offset: int) -> None:
        """
        The backward scan is implemented by moving the file pointer all the way to the front of the current file
        descriptor, and checking if the movement has gone far enough.  If more to go, move to the previous file,
        and repeat.  If too far, seek forward again to the correct position.
        :param offset:
        :return:
        """
        # This is a negative value.
        remaining = offset
        # Remaining is a negative amount, because the scan is going backwards.
        while remaining < 0:
            trace("Scanning backward.  Offset: {}, Remaining: {}".format(offset, remaining))
            start_pos = self._current_file_desc.tell()
            self._current_file_desc.seek(0, 0)
            end_pos = self._current_file_desc.tell()
            # This is a negative value
            moved = end_pos - start_pos
            if moved < remaining:
                # Overshot the backup.  Move forward again.
                corrective_seek = -(moved - remaining)
                self._current_file_desc.seek(corrective_seek, 1)
                end_pos = self._current_file_desc.tell()
                moved = end_pos - start_pos
                # It moved forwards, but `moved` is still negative, because it holds the net movement in this loop.
                self._told += moved
                remaining = 0
            else:
                # It moved backwards, and `moved` is negative.
                remaining -= moved
                self._told += moved
                # The generator for advancing file descriptors will ensure the pointer is at the tail of the file part
                if not self._safe_advance_file_desc(_BACKWARD):
                    break
        trace("Out of loop.  Tell: {}  File tell {}".format(self._told, self._current_file_desc.tell()))

    def _seek_to_head(self) -> None:
        """
        Set the position to zero, tell to zero, and at the head of the first file.

        No need to traverse the list and move through the intermediaries, as the zero position is always known.
        :return:
        """
        trace("Seek to head")
        self._current_file_desc_idx = 0
        self._current_file_desc = self._file_desc_generator.send(_STATIONARY)
        self._current_file_desc.seek(0, 0)
        self._told = 0

    def _seek_to_tail(self) -> None:
        """
        Unlike a true file-like object, zipping to the end will omit some information.  Must open each file, in order,
        and skip to their end, to count the individual file sizes, all the way to the end of that list.

        This may be slow if the disk is slow.

        This process could be accelerated by doing a one-time pass and counting the file sizes directly, but this may
        not be desirable.  In practice, `seek(x, 2)` is rare, used by ZipFile, and even then, just at the start.
        :return: Nothing
        """
        # self._seek_to_head()
        trace("Start of seek to tail.  Tell: {}".format(self._told))
        while True:
            trace("Current IDX: {}".format(self._current_file_desc_idx))
            # Save starting position, might not be zero.
            start = self._current_file_desc.tell()
            # The generator for advancing file descriptors will ensure the pointer is at the start of the file part.
            # Go to the end.
            self._current_file_desc.seek(0, 2)
            # Check position
            end = self._current_file_desc.tell()
            # Keep count of the file sizes.
            self._told += end - start
            # Don't roll off the last one.
            if not self._safe_advance_file_desc(_FORWARD):
                break
        trace("End of seek to tail.  Tell: {}, cfd tell {}".format(self._told, self._current_file_desc.tell()))

    def _safe_advance_file_desc(self, direction) -> bool:
        """
        Advance the file descriptor, but do not advance off the end, either way.

        Return true if advanced, False if stalled.
        :param direction: Backward -1, Stationary 0, Forward 1, or Closing 2.
        :return: Whether or not the _current_file_desc was changed.  False indicates end of file, either end.
        """
        if (direction == _FORWARD and self._current_file_desc_idx + 1 >= len(self._files)) or (
            direction == _BACKWARD and self._current_file_desc_idx <= 0
        ):
            return False
        else:
            self._advance_file_desc(direction)
            return True

    def _advance_file_desc(self, direction) -> None:
        """
        Move the file actual file descriptor around, to allow this class to continue to act as a single file-like reader
        Fix the file pointer position to either the start or end of the underlying real file, depending on the
        direction of movement.
        To close, call `close()` directly on the generator.
        :param direction: Backward -1, Stationary 0, Forward 1
        :return: Nothing, but does set the _current_file_desc.  May set it to None if reading or seeking off either end.
        """
        try:
            self._current_file_desc = self._file_desc_generator.send(direction)
            # Force the file pointer to the front ot the file.  This should be a given.
            if direction == _BACKWARD:
                self._current_file_desc.seek(0, 2)
            # If going backwards, need to make sure that the rollover put the file pointer at the _end_ of the file,
            # not the start.
            elif direction == _FORWARD:
                self._current_file_desc.seek(0, 0)
        except StopIteration:
            self._current_file_desc = None

    def _generate_next_file(self, direction=_FORWARD) -> typing.Generator[typing.BinaryIO, int, None]:
        """
        Only call from `_advance_file_desc`, or, `_seek_to_head` for shortcut operation.
        Only create in `__init__`

        `send()` the direction of travel to this generator.  Backward -1, Stationary 0, Forward 1, or Closing 2.

        This can raise a `FileNotFoundError`, and as such may propagate up through `seek` or `read`

        Using this generator allows the context manager to open and close the file pointers automatically when required.

        :yield: A file-like object for the underlying OS.
        """
        while True:
            self._current_file_desc_idx += direction
            if self._current_file_desc_idx < 0 or self._current_file_desc_idx >= len(self._files):
                debug("Moved off end of files list.  No current fd.")
                direction = yield None
            else:
                file = self._files[self._current_file_desc_idx]
                # This logic is boosted right out of the zipfile.ZipFile.__init__, which takes either a filepath,
                # path-like, or file-like for its `file` argument.
                # Check if we were passed a path-like object
                if isinstance(file, os.PathLike):
                    file = os.fspath(file)
                if isinstance(file, str):
                    # No, it's a filename
                    self._filePassed = 0
                    self.filename = file
                    with open(file, "rb") as self._current_file_desc:
                        debug("Opening new fd on {}".format(file))
                        direction = yield self._current_file_desc
                        debug("Closing fd on {}".format(file))
                else:
                    # No, its (probably) already file-like.
                    self._current_file_desc = file
                    debug("Passthrough file-like yielding {}".format(file))
                    direction = yield self._current_file_desc
                    debug("Passthrough file-like done {}".format(file))

    def test_all_readable(self):
        """
        Validate every file in the `files` parameter at `__init__` is actually readable.

        Seeks to beginning of file list, then opens each file in read-only mode, seeks to the end of each of them, then
        back to current position.  Will raise `IOError` or `FileNotFoundError` or other, appropriate error for files
        that cannot be opened for reading and seeking.

        :return:
        """
        if self._stream_only:
            raise IOError("Seek performed on a streaming file.")

        saved_tell = self._told
        self._seek_to_head()
        self._seek_to_tail()
        self.seek(saved_tell, 0)

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
        """
        Closes the existing file descriptor, sets the current file descriptor to None, and disables the ability to
        seek or read.

        :return:
        """
        debug("Closing last file descriptor.")
        self._file_desc_generator.close()
        self._current_file_desc = None

    @property
    def closed(self) -> bool:
        """
        Checks the status of the underlying streams.  If there is no open File Descriptor attached to any file in the
        list, then this object is closed.
        :return: If there are no available file descriptors for reading, returns True.
        """
        return self._current_file_desc is None

    def __iter__(self) -> typing.Iterable:
        """
        :return: Itself, as an iterable.
        """
        # Iterable operation implies streaming mode, logically, although there is not a technical reason why this
        # module could not permit a seek() between calls to __iter__.
        self._stream_only = True
        return self

    def set_iter_size(self, iter_size: int = 1) -> None:
        """
        :param iter_size: The size of the data returned by a next() call to this object.  This is typically 1, but may
                be any positive integer.  A value of zero will read the entire file on the next call.
        :return: None
        """
        self._iter_size = iter_size

    def __next__(self) -> typing.AnyStr:
        """
        Performs a `read(iter_size)` call, where `set_iter_size` can be called at any time.  Typically just one byte.
        :return: Data, equivalent to `read(iter_size)`
        """
        if not self._stream_only:
            raise IOError("Not in streaming mode.")
        read = self.read(self._iter_size)
        if not read:
            raise StopIteration
        return read

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        from json import dumps

        try:
            # Might be closed, or might be an empty list.
            cfile = dumps(self._files[self._current_file_desc_idx])
            ctell = self._current_file_desc.tell()
            cdesc = self._current_file_desc.fileno()
        except IndexError:
            cfile = None
            ctell = 0
            cdesc = 0

        return "<{cls}, {id}: Tell: {tell}, File Desc: {fdesc}, File Name: {fname}, File Tell: {ftell}>".format(
            cls=self.__class__.__name__, id=hex(id(self)), tell=self.tell(), fdesc=cdesc, fname=cfile, ftell=ctell
        )

    """
    The following methods exist to support the io.RawIO behavior, and mostly disables their use.
    
    This permits the SplitFileReader to work within a context that expects the io.IOBase capabilities, such as a 
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
        """
        Pass-through to the underlying file descriptor.  May not have any consistent meaning after any read or seek
        actions.
        :return:
        """
        if self._current_file_desc:
            return self._current_file_desc.fileno()
        raise IOError("No current file descriptor in use.")

    def readline(self, size: int = ...) -> bytes:
        raise io.UnsupportedOperation(
            "{} cannot decode text, and therefore cannot readline.".format(self.__class__.__name__)
        )

    def readlines(self, hint: int = ...) -> typing.List[bytes]:
        raise io.UnsupportedOperation(
            "{} cannot decode text, and therefore cannot readlines.".format(self.__class__.__name__)
        )
