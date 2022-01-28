from abc import *


class BaseManagement(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass

    @abstractmethod
    def _local_filesystem_user_interfaces(self):
        pass

    @abstractmethod
    def _remote_filesystem_user_interfaces(self):
        pass

    @abstractmethod
    def _local_search(self):
        pass

    @abstractmethod
    def _remote_search(self):
        pass

    @abstractmethod
    def loading_connection(self):
        pass

    @abstractmethod
    def storing_connection(self):
        pass


