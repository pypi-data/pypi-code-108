from abc import ABC, abstractmethod


class Reader(ABC):
    @abstractmethod
    def run(self):
        pass
