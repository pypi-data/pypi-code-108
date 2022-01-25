"""
Complete 'file' implementations which read and write data in chunks.  Main intention is to make remote files accessed
via REST APIs look like local files.  Contains support for restartable uploads (i.e. on s3).
"""
import io
import inspect


class ChunkedFileReader(io.RawIOBase):
    """
    Makes a file-like read-only object from a function that can read chunks.
    """
    def __init__(self, filename: str, reader: callable, mode: str='r', chunk_size=16384, on_close: callable=None, metadata: dict=None, size=None):
        """
        :param filename:    Name to show in the 'name' property.
        :param reader:      Method which accepts a byte range.
        :param mode:        'r' or 'rb'.
        :param metadata:    Additional information to associate with the file (i.e. custom extensions).
        :param size:        Size of file, if known, or None, or a callable.
        """
        self.name = filename
        self.metadata = metadata
        self._size = size
        self._mode = mode
        self._reader = reader
        self._on_close = on_close
        self._pos = 0
        self._offset = 0
        self._chunk = None
        self._eof = False
        self._eol = b'\n' if 'b' in mode else '\n'
        self._min_chunk = chunk_size
        self._max_read = 1048576*1024*1024
        self._output_type = bytearray if 'b' in self._mode else str
        self._is_binary = 'b' in self._mode

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return False

    def seekable(self):
        return True

    def __getitem__(self, item):
        if not isinstance(item, slice):
            item = slice(item, item+1)
        # limit to a particular line range
        return slicer(self, item)

    def _fix_chunk(self, chunk):
        if 'b' in self._mode:
            if isinstance(chunk, str):
                # str -> bytes
                chunk = chunk.encode("utf-8")
        else:
            if isinstance(chunk, bytes):
                # bytes -> str
                chunk = chunk.decode("utf-8")
        return chunk

    def _get_size(self):
        if self._size is None:
            return
        if hasattr(self._size, "__call__"):
            self._size = self._size()
        return self._size

    def __iter__(self):
        """
        Read lines.
        """
        flush = self._chunk is None
        out = self._output_type()
        while True:
            if flush:
                self._chunk = self._fix_chunk(self._reader(self._pos, self._pos + self._min_chunk))
                self._offset = 0
                self._eof = self._eof or not self._chunk or len(self._chunk) < self._min_chunk
                flush = False
            try:
                eol2 = self._chunk.index(self._eol, self._offset)
                out += self._chunk[self._offset:eol2]
                eol2 += len(self._eol)
                self._pos += eol2 - self._offset
                self._offset = eol2
                yield out
                out = self._output_type()
            except ValueError:
                # EOL not found in chunk
                out += self._chunk[self._offset:]
                if self._eof:
                    if out:
                        yield out
                    break
                self._pos += len(self._chunk) - self._offset
                self._offset = len(self._chunk)
                flush = True

    def _read_direct(self, n):
        self._offset = 0
        self._chunk = None
        out = self._fix_chunk(self._reader(self._pos, self._pos + n))
        self._pos += len(out)
        if len(out) < n:
            self._eof = True
        return out

    def read(self, n=None):
        if not n or n > self._max_read:
            return self.read(self._max_read)
        # read large chunks directly, no buffer
        if n >= self._min_chunk*2 and not self._eof and not self._offset:
            return self._read_direct(n)
        out = self._output_type()
        while True:
            # make sure we have a chunk
            if (self._chunk is None or self._offset >= len(self._chunk)) and not self._eof:
                self._chunk = self._fix_chunk(self._reader(self._pos, self._pos + self._min_chunk))
                self._eof = not self._chunk or len(self._chunk) < self._min_chunk
                self._offset = 0
            if not self._chunk:
                break
            # take what we can from this chunk
            part = self._chunk[self._offset: self._offset + n]
            out += part
            n -= len(part)
            self._pos += len(part)
            self._offset += len(part)
            if n <= 0 or self._eof:
                break
        if self._is_binary:
            # NOTE: some code (i.e. pandas.read_csv()) assumes 'bytes' and fails on 'bytearray'
            return bytes(out)
        return out

    def tell(self):
        return self._pos

    def seek(self, n: int, whence: int=None):
        if whence == 2:
            if self._eof:
                if n >= 0:
                    return
                n += self._pos
            else:
                size = self._get_size()
                if size is None:
                    raise Exception("not supported, seek(*, 2) except at EOF")
                n += size
            whence = 0
        if whence == 1:
            n += self._pos
        if self._chunk is not None:
            buf0 = self._pos - self._offset
            buf_n = buf0 + len(self._chunk)
            if buf0 <= n < buf_n:
                # seek is within current chunk
                o2 = n - buf0
                self._pos += o2 - self._offset
                self._offset = o2
                self._eof = False
                return
        self._pos = n
        self._chunk = None
        self._eof = False

    def close(self):
        if self._on_close:
            self._on_close()


class ChunkedFileWriter(object):
    """
    Makes a file-like writable object from a function that can write/append chunks.

    The writer() method takes 2-3 arguments: the data to write, an 'append' flag, and then optionally a 'hint'
    flag.

    The normal/simple implementation only defines the first two flags.  Assuming only one process is
    updating a given file at one time, and assuming the requests arrive in order, appending works for
    transmission of large files.  In this implementation there is no return value from writer().

    The 'hint' flag is required to bypass those limitations.  Here is how a multi-part upload works using such
    an implementation:
      upload_id = writer(FIRST_CHUNK, False, hint="start:TOTAL_FILE_SIZE")
      writer(SECOND_CHUNK, True, hint="continue:UPLOAD_ID:1")
      writer(...)
      writer(LAST_CHUNK, True, hint="end:UPLOAD_ID:N")
    """
    def __init__(self, filename: str, writer: callable, mode: str='w', chunk_size=10000000, metadata: dict=None, total_size: int=None):
        """
        :param filename:    Name to show in the 'name' property.
        :param writer:      Method which writes data of the type indicated by mode.
        :param mode:        'w' or 'wb'.
        :param chunk_size:  How much data to write at once.  Note that for S3 the minimum is 5Mi.
        :param metadata:    Additional information to associate with the file (i.e. custom extensions).
        :param total_size:  Total size of data being transferred, if known.
        """
        self.name = filename
        self.metadata = metadata
        self._mode = mode
        self._writer = writer
        self._can_hint = "hint" in inspect.signature(writer).parameters.keys()
        self._append = 'a' in mode
        self._buffer = bytearray() if 'b' in mode else ""
        self._chunk_size = chunk_size
        self._chunk_no = 0
        self._mpu_id = None
        self._total_size = total_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def seekable(self):
        return False

    def write(self, content):
        if isinstance(content, str) == ('b' in self._mode):
            raise TypeError("invalid data type for mode=%s" % self._mode)
        while len(self._buffer) + len(content) >= self._chunk_size:
            part = self._chunk_size - len(self._buffer)
            self._buffer += content[:part]
            self.flush()
            content = content[part:]
        self._buffer += content

    def flush(self, last: bool=False):
        if self._buffer or last:
            self._chunk_no += 1
            single_chunk = self._chunk_no == 1 and last
            if self._can_hint and not single_chunk:
                hint, phase = self._hint_phase(last)
                resp = self._writer(self._buffer, self._append, hint=hint)
                if phase == "start":
                    self._mpu_id = resp
            else:
                self._writer(self._buffer, self._append)
            self._append = True
            self._buffer = bytearray() if 'b' in self._mode else ""

    def _hint_phase(self, last: bool):
        if self._chunk_no == 1:
            phase = "start"
        else:
            phase = "end" if last else "continue"
        if phase == "start":
            hint = "start:%d" % (self._total_size or -1)
        elif self._mpu_id:
            hint = "%s:%s:%d" % (phase, self._mpu_id, self._chunk_no - 1)
        else:
            hint = None
        return hint, phase

    def close(self):
        self.flush(last=True)


def slicer(iterable, which):
    """
    Supports sliced iteration for another iterator.
    """
    if not isinstance(which, slice):
        which = slice(which, which+1)
    # reject negative start/stop/step values
    if \
            (which.start is not None and which.start < 0) or \
            (which.stop is not None and which.stop < 0) or \
            (which.step is not None and which.step < 0):
        raise Exception("not allowed: negative slice values")
    # generate an iterable
    return SlicerFetcher(iterable, which)


class SlicerFetcher(object):
    def __init__(self, iterable, which):
        self.iterable = iterable
        self.which = which
        self.pos = -1
        self.item = None

    def __iter__(self):
        i = iter(self.iterable)
        def skip():
            if not self.which.step or self.which.step < 2:
                return
            for _ in range(self.which.step - 1):
                next(i)
        try:
            if self.which.start:
                for _ in range(self.which.start):
                    next(i)
            if self.which.stop is None:
                while True:
                    yield next(i)
                    skip()
            n = self.which.stop - (self.which.start or 0)
            if self.which.step:
                n /= self.which.step
            for _ in range(n):
                yield next(i)
                skip()
        except StopIteration:
            pass
