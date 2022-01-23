"""Абстрактный класс для работы с хранилищами"""
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class EntryType(Enum):
    """EntryType описывает тип файла"""
    FILE = 1
    FOLDER = 2
    LINK = 3


@dataclass
class FileData:
    """FileData описывает файл ftp-сервера"""
    name: str
    size: int = 0
    etype: EntryType = EntryType.FILE
    time: datetime = datetime.now()

    def __init__(
        self, name: str, size: int = 0,
        etype: EntryType = EntryType.FILE,
        time: datetime = datetime.now(),
    ) -> None:
        self.name = name
        self.size = size
        self.etype = etype
        self.time = time


class Storage(ABC):
    """Storage базовый класс для работы с хранилищами"""
    @abstractmethod
    def files(self, path: str) -> ([FileData], bool):
        """upload загружает файл source в Storage"""

    @abstractmethod
    def upload(self, source: str, destination: str) -> bool:
        """upload загружает файл source в Storage"""

    @abstractmethod
    def download(self, source: str, destination: str) -> bool:
        """download скачивает файл source из Storage"""
