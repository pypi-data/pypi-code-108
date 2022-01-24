import pickle
import multiprocessing
import os

from typing.io import BinaryIO
from .reader import Reader


def inner_read_task_meta(arg):
    offset, n_batches, mount_path, seek_offset, data_lens, batch_queue = arg

    with open(mount_path, "rb", os.O_DIRECT) as file:
        file.seek(seek_offset, 0)
        for i_batches in range(n_batches):
            batch = pickle.loads(bytes(list(file.read(data_lens[i_batches]))))
            batch_queue.put(batch)


"""
Data format:

Files: gpu_0 + meta_0

meta_0: bytes count in batch_0, bytes count in batch_1, ...
gpu_0: raw batches bytes

"""


class OptimizedMultiprocessingReader(Reader):
    def __init__(self, batch_queue, n_batches, data_path, meta_path, processes=1):
        self.batch_queue = batch_queue
        self.n_batches = n_batches
        self.data_path = data_path
        self.meta_path = meta_path
        self.processes = processes

        self.pool = multiprocessing.Pool(self.processes)

        # offsets[i] == offset required for start read from batch i
        self._offsets = [0]
        # data_lens[i] == bytes count to read from offsets[i]
        self._data_lens = []

    def run(self):
        self._offsets = [0]
        self._data_lens = []
        with open(self.meta_path, "rb", os.O_DIRECT) as meta:
            try:
                for _ in range(self.n_batches):
                    data_len = int.from_bytes(meta.read(4), byteorder='big')
                    self._offsets.append(self._offsets[-1] + data_len)
                    self._data_lens.append(data_len)

            except Exception as e:
                pass

        tasks = [self.resolve_range(i) for i in range(self.processes)]
        self.pool.map(inner_read_task_meta, tasks)

    # (off, count)
    def resolve_range(self, thread_idx):
        batches_per_process = self.n_batches / self.processes
        cur_off = int(thread_idx * batches_per_process)
        next_off = int((thread_idx + 1) * batches_per_process)
        next_off = min(self.n_batches, next_off)
        return cur_off, next_off - cur_off, self.data_path, self._offsets[cur_off], self._data_lens[cur_off:next_off], self.batch_queue
