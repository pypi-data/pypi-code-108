from abc import ABCMeta, abstractmethod

class FileProcessor(metaclass=ABCMeta):
    @abstractmethod
    def process(self, file_path: str) -> None:
        pass

