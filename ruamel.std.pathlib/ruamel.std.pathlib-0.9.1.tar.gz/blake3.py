# this fails immediately on import of ruamel.std.pathlib.blake3 if blake3 not installed
from blake3 import blake3

from pathlib import Path

if not hasattr(Path, 'blake3'):

    def _blake3(self, size=-1, timeit=False):
        """blake3 hash of the contents
        if size is provided and non-negative only read that amount of bytes from
        the start of the file
        """
        with self.open(mode='rb') as f:
            data = f.read(size)
        if timeit:
            import time

            start = time.time()
            try:
                res = blake3(data, max_threads=blake3.AUTO)
            except TypeError:
                res = blake3(data, multithreading=True)
            return time.time() - start, res
        try:
            res = blake3(data, max_threads=blake3.AUTO)
        except TypeError:
            res = blake3(data, multithreading=True)
        return res

    Path.blake3 = _blake3
