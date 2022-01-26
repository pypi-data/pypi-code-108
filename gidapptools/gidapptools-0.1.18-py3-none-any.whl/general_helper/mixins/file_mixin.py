"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from enum import unique
from typing import Union, AnyStr, Literal
from hashlib import md5, sha256, blake2b, blake2s, sha3_512
from pathlib import Path
from threading import Event, RLock

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.enums import BaseGidEnum
from gidapptools.gid_signal.interface import get_signal
from gidapptools.general_helper.conversion import human2bytes

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()


# endregion[Constants]


READ_TYPE = Union[Literal["r"], Literal["rb"]]
WRITE_TYPE = Union[Literal["w"], Literal["wb"], Literal['a'], Literal['ab']]
ON_ERRORS_TYPE = Union[Literal['replace'], Literal['ignore'], AnyStr]
HASH_FUNC_TYPE = Union[blake2b, md5, sha256, sha3_512, blake2s]


class FileMixin(os.PathLike):
    _encoding = 'utf-8'
    _on_errors: ON_ERRORS_TYPE = 'ignore'

    hash_func: HASH_FUNC_TYPE = md5
    file_hash_size_threshold: int = human2bytes("100 mb")
    path_locks: dict[Path, RLock] = {}
    path_events: dict[Path, Event] = {}

    @unique
    class ChangeParameter(BaseGidEnum):
        SIZE = "size"
        FILE_HASH = "file_hash"
        CHANGED_TIME = "changed_time"
        ALWAYS = "always"
        NEVER = "never"
        ALL = "all"

    def __init__(self, file_path: Path, changed_parameter: str = None, **kwargs) -> None:
        self.file_path = Path(file_path)
        self.name = self.file_path.name.casefold()
        self.changed_parameter = self.ChangeParameter.SIZE if changed_parameter is None else self.ChangeParameter(changed_parameter)
        self.read_mode: READ_TYPE = 'r'
        self.write_mode: WRITE_TYPE = 'w'
        self.last_size: int = None
        self.last_file_hash: str = None
        self.last_changed_time: int = None
        self.changed_signal = get_signal(key=self.file_path)
        super().__init__(**kwargs)

    def set_changed_parameter(self, changed_parameter: Union["ChangeParameter", str]) -> None:
        if isinstance(changed_parameter, self.ChangeParameter):
            self.changed_parameter = changed_parameter
        else:
            self.changed_parameter = self.ChangeParameter(changed_parameter)

    @property
    def lock(self) -> RLock:
        if self.file_path not in self.path_locks:
            self.path_locks[self.file_path] = RLock()
        return self.path_locks[self.file_path]

    @property
    def disable_read_event(self) -> Event:
        if self.file_path not in self.path_events:
            self.path_events[self.file_path] = Event()
        return self.path_events[self.file_path]

    @property
    def size(self) -> int:
        size = self.file_path.stat().st_size
        return size

    @property
    def file_hash(self) -> str:

        with self.file_path.open('rb') as f:
            if self.size <= self.file_hash_size_threshold:

                return self.hash_func(f.read()).hexdigest()
            _file_hash = self.hash_func()
            for chunk in f:
                _file_hash.update(chunk)
            return _file_hash.hexdigest()

    @property
    def changed_time(self) -> int:
        return self.file_path.stat().st_mtime

    @property
    def has_changed(self) -> bool:
        if self.disable_read_event.is_set() is True:
            return False

        def on_size() -> bool:
            return self.last_size is None or self.last_size != self.size

        def on_file_hash() -> bool:
            return self.last_file_hash is None or self.last_file_hash != self.file_hash

        def on_time() -> bool:
            return self.last_changed_time is None or self.last_changed_time != self.changed_time

        def on_all() -> bool:
            return any([on_size(), on_file_hash(), on_time()])

        def on_always() -> bool:
            return True

        def on_never() -> bool:
            return False
        checks = {self.ChangeParameter.SIZE: on_size,
                  self.ChangeParameter.FILE_HASH: on_file_hash,
                  self.ChangeParameter.CHANGED_TIME: on_time,
                  self.ChangeParameter.ALL: on_all,
                  self.ChangeParameter.ALWAYS: on_always,
                  self.ChangeParameter.NEVER: on_never}
        with self.lock:
            result = checks[self.changed_parameter]()
            if result is True:
                self.changed_signal.emit(self)
        return result

    def _update_changed_data(self) -> None:

        def _update_size():
            self.last_size = self.size

        def _update_file_hash():
            self.last_file_hash = self.file_hash

        def _update_changed_time():
            self.last_changed_time = self.changed_time

        def _update_all():
            _update_size()
            _update_file_hash()
            _update_changed_time()
        update_table = {self.ChangeParameter.NEVER: lambda: ...,
                        self.ChangeParameter.ALWAYS: lambda: ...,
                        self.ChangeParameter.SIZE: _update_size,
                        self.ChangeParameter.FILE_HASH: _update_file_hash,
                        self.ChangeParameter.CHANGED_TIME: _update_changed_time,
                        self.ChangeParameter.ALL: _update_all}
        update_table[self.changed_parameter]()

    @property
    def _read_kwargs(self) -> dict[str, str]:
        kwargs = {"mode": self.read_mode}
        if 'b' not in self.read_mode:
            kwargs['encoding'] = self._encoding
            kwargs['errors'] = self._on_errors
        return kwargs

    @property
    def _write_kwargs(self) -> dict[str, str]:
        kwargs = {"mode": self.write_mode}
        if 'b' not in self.write_mode:
            kwargs['encoding'] = self._encoding
            kwargs['errors'] = self._on_errors
        return kwargs

    def read(self):
        with self.lock:
            self._update_changed_data()
            # pylint: disable=unspecified-encoding
            with self.file_path.open(**self._read_kwargs) as f:
                return f.read()

    def write(self, data) -> None:
        with self.lock:
            # pylint: disable=unspecified-encoding
            with self.file_path.open(**self._write_kwargs) as f:
                f.write(data)

    # def __getattr__(self, name: str) -> Any:
    #     if hasattr(self.file_path, name):
    #         return getattr(self.file_path, name)
    #     return super().__getattr__(name)

    def __fspath__(self) -> str:
        return str(self.file_path)

    def __str__(self) -> str:
        return self.__fspath__()
# region[Main_Exec]


if __name__ == '__main__':
    pass
# endregion[Main_Exec]
