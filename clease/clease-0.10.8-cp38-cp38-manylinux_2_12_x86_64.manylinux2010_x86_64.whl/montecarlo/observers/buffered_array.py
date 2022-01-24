from typing import Union
from pathlib import Path
import numpy as np

__all__ = ('BufferedArray',)


class BufferedArray:
    """
    Implement a cyclic buffer. If fname, is given the buffer is flushed to
    file when full.

    :param size: Size of the buffer
    :param fname: Filename where the buffer will be written when full. If None,
        the buffer will not be flushed to file when full.
    """

    def __init__(self, size: int = 1000, fname: Union[str, Path] = None):
        self._buffer = np.zeros(size)
        self._next = 0
        self.fname = fname

    def flush(self):
        if self.fname is not None:
            with open(self.fname, 'a') as f:
                np.savetxt(f, self._buffer)
        self._next = 0
        self._buffer[:] = 0

    def _flush_if_full(self) -> None:
        """
        Flush buffer to backup file when the buffer is full. If no file is
        given, this function simply resets the buffer to zeros.
        """
        if self._next < len(self._buffer):
            return
        self.flush()

    def push(self, v: float) -> None:
        """
        Insert a new value at the end of the buffer. The buffer is automatically
        flushed if full.

        :param v: New value to insert.
        """
        self._flush_if_full()
        self._buffer[self._next] = v
        self._next += 1

    def clear(self):
        """
        Clear array
        """
        self._buffer[:] = 0
        self._next = 0
