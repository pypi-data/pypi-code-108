import pickle
from typing.io import BinaryIO
from .reader import Reader


class SimpleReader(Reader):
    def __init__(self, batch_queue, n_batches, mount_path):
        self._batch_queue = batch_queue
        self._n_batches = n_batches
        self._mount_path = mount_path

    def run(self):
        i_batches = 0
        with open(self._mount_path, mode="rb") as file:
            while i_batches < self._n_batches:
                batch = self.__read_batch_from_file(
                    file=file
                )
                i_batches += 1
                self._batch_queue.put(batch)

    def __read_batch_from_file(self, file: BinaryIO):
        int.from_bytes(file.read(4), byteorder='big')
        topic_len = int.from_bytes(file.read(2), byteorder='big')
        file.read(topic_len).decode("utf-8")
        data_len = int.from_bytes(file.read(4), byteorder='big')
        batch = pickle.loads(bytes(list(file.read(data_len))))
        return batch
