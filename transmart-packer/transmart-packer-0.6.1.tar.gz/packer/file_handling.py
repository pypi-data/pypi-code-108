import abc
import os

from packer.config import task_config


class FileHandlerABC(metaclass=abc.ABCMeta):

    def __init__(self, task_id):
        self.task_id = task_id

    @abc.abstractmethod
    def exists(self):
        """ Returns True if the resource exists, else False """

    @property
    @abc.abstractmethod
    def reader(self):
        """ Return file-like object for reading """

    @property
    @abc.abstractmethod
    def byte_reader(self):
        """ Return file-like object for reading in byte mode """

    @property
    @abc.abstractmethod
    def writer(self):
        """ Return file-like object for writing """


class FSHandler(FileHandlerABC):
    """
    Provide method for reading and writing the output file of a task to filesystem.
    """

    @property
    def path(self):
        return os.path.join(task_config['data_dir'], self.task_id)

    def _handler(self, mode):
        return open(self.path, mode)

    def exists(self):
        return os.path.exists(self.path)

    @property
    def reader(self):
        return self._handler('r')

    @property
    def byte_reader(self):
        """ Read file as bytes. """
        return self._handler('rb')

    @property
    def writer(self):
        return self._handler('wb')
