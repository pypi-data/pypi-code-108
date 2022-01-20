from abc import *

class DatabaseAccessObject(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def installation_guide(self):
        pass

    @abstractmethod
    def meta_information(self):
        pass

    @abstractmethod
    def connection(self):
        pass

    @abstractmethod
    def execute(self):
        pass
