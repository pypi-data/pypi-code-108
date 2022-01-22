import subprocess
from abc import ABC, abstractmethod
from pathlib import Path


class Provider(ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError("Provider should implement a start method.")

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError("Provider should implement a stop method.")

    @abstractmethod
    def is_running(self) -> bool:
        raise NotImplementedError("Provider should implement an is_running method.")


class ZaproxyProvider(Provider, ABC):
    """Provides information about a running ZAP instance."""

    @property
    @abstractmethod
    def ip(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def port(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def home_directory(self) -> Path:
        raise NotImplementedError

    @property
    @abstractmethod
    def api_key(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def process(self) -> subprocess.Popen[bytes]:
        raise NotImplementedError
