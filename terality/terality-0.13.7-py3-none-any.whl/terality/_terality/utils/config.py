import os
from typing import Type, TypeVar

from abc import ABC
from pathlib import Path
from typing import ClassVar, Tuple

from pydantic import BaseModel, BaseSettings, Field  # pylint: disable=no-name-in-module


class _Paths(BaseSettings):
    terality_home: Path = Field(Path.home() / ".terality", env="TERALITY_HOME")


T = TypeVar("T", bound="BaseConfig")


class BaseConfig(BaseModel, ABC):
    """Base abstract class for configuration objects that can be stored in configuration files."""

    _rel_path: ClassVar[str]  # path to the configuration file relative to `$TERALITY_HOME`
    _permissions: ClassVar[int] = 0o644  # rw-r--r--

    @classmethod
    def file_path(cls) -> Path:
        return _Paths().terality_home / cls._rel_path

    @classmethod
    def load(cls: Type[T], fallback_to_defaults: bool = False) -> T:
        """Load the configuration object from the underlying file.

        Args:
            fallback_to_defaults: if True, return a default configuration file when the file does
                not already exists, or if any error occurs when reading it

        Return:
            a configuration object

        Raise:
            Exception: if the file can not be found (when fallback_to_defaults is False)
        """
        file_path = cls.file_path()
        try:
            return cls.parse_file(file_path)
        except Exception:  # pylint: disable=broad-except
            # TODO: use a less generic exception
            if not fallback_to_defaults:
                raise
            return cls()

    def save(self) -> None:
        file_path = self.file_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(
            os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode=self._permissions),
            "w",
        ) as f:
            f.write(self.json(indent=4))


class TeralityCredentials(BaseConfig):
    """User authentication information."""

    _rel_path: ClassVar[str] = "credentials.json"
    _permissions: ClassVar[int] = 0o600  # rw-------
    user_id: str  # Client-facing user ID (probably an email). Note that the "server user ID" is different.
    user_password: str  # API key or similar


_PRODUCTION_URL = "api.terality2.com/v1"


class TeralityConfig(BaseConfig):
    """Generic configuration related to the Terality API.

    The default values are suitable for the production SaaS environment.
    """

    _rel_path: ClassVar[str] = "config.json"
    url: str = _PRODUCTION_URL
    use_https: bool = True
    requests_ssl_verification: bool = (
        True  # note: this parameter is mostly ignored right now, and will probably be deprecated
    )
    timeout: Tuple[int, int] = (3, 35)  # The server has a max 30s timeout on responses.
    is_demo: bool = False

    # Legacy - the URL parameter should contain everything, but we don't want to invalidate all
    # existing configuration files, nor (for now) deal with multiple configuration versions.
    def full_url(self):
        prefix = "https" if self.use_https else "http"
        return f"{prefix}://{self.url}"

    @property
    def ignore_session(self) -> bool:
        return self.is_demo

    @property
    def skip_transfers(self) -> bool:
        return self.is_demo

    @property
    def is_production(self) -> bool:
        return self.url == _PRODUCTION_URL
