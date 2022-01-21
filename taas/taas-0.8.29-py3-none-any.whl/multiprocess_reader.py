import pickle
import multiprocessing
import os
import sys

from typing.io import BinaryIO
from .reader import Reader


def inner_read_batch_from_file(file: BinaryIO):
    int.from_bytes(file.read(4), byteorder='big')
    topic_len = int.from_bytes(file.read(2), byteorder='big')
    file.read(topic_len).decode("utf-8")
    data_len = int.from_bytes(file.read(4), byteorder='big')
    batch = pickle.loads(bytes(list(file.read(data_len))))
    return batch


def inner_read_task(arg):
    offset, n_batches, mount_path, batch_queue = arg
    i_batches = 0
    i = 0
    with open(mount_path, "rb", os.O_DIRECT) as file, open(f"/tmp/pid_{os.getpid()}", "w") as log_f:
        try:
            log_f.write(f'{offset} {n_batches} {mount_path} {batch_queue}\n')
            while i < offset:
                int.from_bytes(file.read(4), byteorder='big')
                topic_len = int.from_bytes(file.read(2), byteorder='big')
                file.read(topic_len)
                data_len = int.from_bytes(file.read(4), byteorder='big')
                file.seek(data_len, 1)
                i += 1
            # log_f.write(f'SKIPPING BATCHES DONE\n')
            while i_batches < n_batches:
                batch = inner_read_batch_from_file(file=file)
                i_batches += 1
                # log_f.write(f'before put {i_batches}')
                batch_queue.put(batch)
                # log_f.write(f'after put {i_batches}')
        except Exception as e:
            log_f.write(str(e) + "\n")


class MultiprocessingReader(Reader):
    def __init__(self, batch_queue, n_batches, mount_path, processes=1):
        self._batch_queue = batch_queue
        self._n_batches = n_batches
        self._mount_path = mount_path
        self._processes = processes

        self._pool = multiprocessing.Pool(self._processes)

    def run(self):
        with open("/tmp/reader.log", "w") as run_log:
            offsets = [self.resolve_range(i) for i in range(self._processes)]

            run_log.write(str(list(map(lambda x: x[0], offsets))))
            run_log.write(str(list(map(lambda x: x[1], offsets))))
            run_log.write("\n")
            self._pool.map(inner_read_task, offsets)
            run_log.write("\npool read map done\n")

    # (off, count, mount_path, queue)
    def resolve_range(self, i):
        cur_off = int(i * (self._n_batches / self._processes))
        next_off = min(self._n_batches, (int((i + 1) * (self._n_batches / self._processes))))
        return cur_off, next_off - cur_off, self._mount_path, self._batch_queue
